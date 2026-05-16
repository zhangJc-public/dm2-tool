"""
RAG Engine - 基于 Obsidian 文件系统的检索增强生成
纯文件系统检索，无需 ChromaDB
"""

import re
from dataclasses import dataclass
from pathlib import Path

from dm2.kernel.indexer import DM2KnowledgeIndexer


@dataclass
class RetrievalResult:
    """检索结果"""
    content: str
    source: str  # 文件路径
    relevance_score: float
    chunk_type: str  # "frontmatter", "body", "term_definition"


@dataclass
class RetrievalContext:
    """检索上下文"""
    query: str
    results: list[RetrievalResult]
    total_tokens: int = 0

    def to_prompt_context(self, max_results: int = 5) -> str:
        """将检索结果转换为 Prompt 上下文"""
        if not self.results:
            return ""

        sections = ["## 检索到的相关知识\n"]

        for i, r in enumerate(self.results[:max_results], 1):
            sections.append(f"### [{i}] {Path(r.source).name}\n")
            sections.append(f"**来源**: {r.source}\n")
            sections.append(f"**内容**:\n{r.content}\n")
            sections.append("---\n")

        return "\n".join(sections)

    def get_all_content(self) -> str:
        """获取所有检索内容（用于 LLM 上下文）"""
        return "\n\n".join(r.content for r in self.results)


class ObsidianRAGEngine:
    """
    基于 Obsidian 文件系统的 RAG 引擎

    检索策略：
    1. frontmatter 属性匹配（dm2-type, dm2-layer 等）
    2. 双链 [[]] 关系图谱遍历
    3. 标签和关键词匹配
    4. 文件名和路径匹配
    """

    def __init__(self, indexer: DM2KnowledgeIndexer):
        self.indexer = indexer

    def retrieve(self, query: str, max_results: int = 5,
                 filters: dict = None) -> RetrievalContext:
        """
        检索与查询相关的知识

        Args:
            query: 用户查询
            max_results: 最大返回结果数
            filters: 过滤条件（如 dm2_type, layer 等）

        Returns:
            RetrievalContext 检索上下文
        """
        query_lower = query.lower()
        results: list[RetrievalResult] = []

        # 1. 从索引获取 DM2 术语匹配
        term_results = self._search_terms(query_lower)
        results.extend(term_results)

        # 2. 从索引获取概念匹配
        concept_results = self._search_concepts(query_lower, filters)
        results.extend(concept_results)

        # 3. 全文搜索 Markdown 文件
        file_results = self._search_files(query_lower, max_results=3)
        results.extend(file_results)

        # 4. 按相关性排序
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        # 5. 去重（同一文件只保留最高分的结果）
        seen_sources = set()
        unique_results = []
        for r in results:
            if r.source not in seen_sources:
                seen_sources.add(r.source)
                unique_results.append(r)

        # 6. 限制结果数
        final_results = unique_results[:max_results]

        # 计算总 token 数（粗略估计）
        total_tokens = sum(len(r.content) // 4 for r in final_results)

        return RetrievalContext(
            query=query,
            results=final_results,
            total_tokens=total_tokens,
        )

    def retrieve_for_view(self, view_id: str, context: str = "") -> RetrievalContext:
        """
        针对特定视图检索相关知识

        Args:
            view_id: DoDAF 视图 ID（如 "OV-5b"）
            context: 额外的上下文信息

        Returns:
            RetrievalContext
        """
        view_template = self.indexer.get_view_template(view_id)
        if not view_template:
            return RetrievalContext(query=f"view={view_id}", results=[])

        # 构建查询
        query_parts = [
            view_id,
            view_template.view_name,
            view_template.viewpoint,
        ]
        query_parts.extend(view_template.dm2_groups)

        if context:
            query_parts.append(context)

        query = " ".join(query_parts)
        return self.retrieve(query, max_results=5)

    def _search_terms(self, query: str) -> list[RetrievalResult]:
        """搜索 DM2 术语"""
        results = []

        for term in self.indexer._terms_cache.values():
            score = 0.0

            # 术语名称匹配
            if query in term.term.lower():
                score += 0.8

            # 别名匹配
            for alias in term.alias:
                if query in alias.lower():
                    score += 0.5
                    break

            # 定义匹配
            if query in term.definition.lower():
                score += 0.3

            if score > 0.1:
                content = f"""**术语**: {term.term}

**定义**: {term.definition}

**别名**: {', '.join(term.alias) if term.alias else '无'}

**来源**: {term.source}

**归属数据组**: {', '.join(term.groups)}
"""
                results.append(RetrievalResult(
                    content=content,
                    source=term.file_path,
                    relevance_score=score,
                    chunk_type="term_definition",
                ))

        return results

    def _search_concepts(self, query: str, filters: dict = None) -> list[RetrievalResult]:
        """搜索 DM2 概念"""
        results = []

        concepts = self.indexer.search_concepts(
            dm2_type=filters.get("dm2_type") if filters else None,
            layer=filters.get("layer") if filters else None,
        )

        for concept in concepts:
            score = 0.0

            # 名称匹配
            if query in concept.name.lower():
                score += 0.7

            # 类型匹配
            if query in concept.dm2_type.lower():
                score += 0.4

            # 定义匹配
            if concept.definition and query in concept.definition.lower():
                score += 0.3

            # 标签匹配
            for tag in concept.tags:
                if query in tag.lower():
                    score += 0.3
                    break

            # 双链中的概念名匹配
            for link in concept.related_links:
                if query in link.lower():
                    score += 0.2
                    break

            if score > 0.1:
                content = f"""**概念**: {concept.name}

**DM2 类型**: {concept.dm2_type}
**分层**: {concept.layer}
**子类型**: {concept.subtype if concept.subtype else '无'}

**定义**: {concept.definition if concept.definition else '无'}

**关系**:
{self._format_relationships(concept.relationships)}

**相关链接**: {', '.join(concept.related_links) if concept.related_links else '无'}

**标签**: {', '.join(concept.tags) if concept.tags else '无'}
"""
                results.append(RetrievalResult(
                    content=content,
                    source=concept.file_path,
                    relevance_score=score,
                    chunk_type="frontmatter",
                ))

        return results

    def _format_relationships(self, relationships: dict) -> str:
        """格式化关系"""
        if not relationships:
            return "无"

        lines = []
        for rel_type, targets in relationships.items():
            if targets:
                lines.append(f"  - {rel_type}: {', '.join(targets)}")
        return "\n".join(lines) if lines else "无"

    def _search_files(self, query: str, max_results: int = 3) -> list[RetrievalResult]:
        """全文搜索 Markdown 文件"""
        results = []
        query_terms = query.split()

        if not self.indexer.reference_root.exists():
            return results

        for md_file in self.indexer.reference_root.rglob("*.md"):
            # 跳过详细分析目录
            if "详细分析" in md_file.parts:
                continue

            score = 0.0

            # 文件名匹配
            filename_lower = md_file.stem.lower()
            for term in query_terms:
                if term in filename_lower:
                    score += 0.5

            # 路径匹配
            path_str = str(md_file).lower()
            for term in query_terms:
                if term in path_str:
                    score += 0.3

            if score > 0.1:
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 提取 frontmatter 和部分正文
                    frontmatter, body = self._split_frontmatter(content)

                    # frontmatter 优先
                    chunk_content = frontmatter if frontmatter else body[:500]

                    results.append(RetrievalResult(
                        content=chunk_content,
                        source=str(md_file),
                        relevance_score=score,
                        chunk_type="frontmatter" if frontmatter else "body",
                    ))
                except Exception:
                    continue

        return results[:max_results]

    def _split_frontmatter(self, content: str) -> tuple[str, str]:
        """分离 frontmatter 和正文"""
        match = re.match(r'^---\n(.*?)\n---(.*)$', content, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return "", content[:1000]

    def expand_via_links(self, concept_name: str, depth: int = 1) -> list[str]:
        """
        通过双链扩展概念集

        Args:
            concept_name: 起始概念名
            depth: 扩展深度

        Returns:
            扩展后的概念列表
        """
        visited = {concept_name}
        current = {concept_name}

        for _ in range(depth):
            next_current = set()
            for name in current:
                concept = self.indexer.get_concept(name)
                if concept:
                    for link in concept.related_links:
                        link_name = Path(link).stem if '/' in link else link
                        if link_name not in visited:
                            visited.add(link_name)
                            next_current.add(link_name)
            current = next_current

        return list(visited)


class RAGContextBuilder:
    """RAG 上下文构建器"""

    def __init__(self, rag_engine: ObsidianRAGEngine):
        self.rag = rag_engine

    def build_for_view_generation(self, view_id: str,
                                  system_description: str) -> str:
        """构建视图生成的上下文"""
        # 检索相关知识
        context = self.rag.retrieve_for_view(view_id, system_description)

        # 构建完整上下文
        sections = [
            f"## 查询\n{system_description}\n",
            context.to_prompt_context(max_results=5),
        ]

        return "\n".join(sections)

    def build_for_analysis(self, query: str) -> str:
        """构建分析查询的上下文"""
        context = self.rag.retrieve(query, max_results=3)
        return context.to_prompt_context(max_results=3)


if __name__ == "__main__":
    indexer = DM2KnowledgeIndexer()
    indexer.load_all()
    engine = ObsidianRAGEngine(indexer)

    # 测试检索
    test_queries = [
        "Performer 活动 执行者",
        "OV-5b 活动追踪",
        "Activity consumes produces resource",
    ]

    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {q}")
        context = engine.retrieve(q, max_results=3)
        print(f"检索到 {len(context.results)} 个结果")
        for r in context.results:
            print(f"  [{r.relevance_score:.2f}] {Path(r.source).name} ({r.chunk_type})")
