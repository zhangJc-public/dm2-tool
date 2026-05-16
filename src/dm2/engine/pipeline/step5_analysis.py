from __future__ import annotations
"""
Step 5: Analysis Execution (分析执行)

四算子:
  1. 溯因推理 (Abductive) — 基于 DM2 8 种模式推断缺失关系
  2. OODA — 检测架构中的决策断点
  3. TOC — 识别资源流瓶颈
  4. 一致性检查 — 复用 consistency.py
"""

import re
from dataclasses import dataclass, field

from dm2.reasoning.patterns import PatternMatcher, PatternType
from dm2.reasoning.consistency import ConsistencyChecker, ConsistencyIssue, IssueSeverity


@dataclass
class AbductiveInference:
    entity_a: str
    entity_b: str
    inferred_relation: str
    confidence: float
    rationale: str


@dataclass
class OODABreakpoint:
    node: str
    missing_phase: str  # Observe/Orient/Decide/Act
    reason: str


@dataclass
class TOCBottleneck:
    node: str
    in_degree: int
    out_degree: int
    impact: str


@dataclass
class AnalysisResult:
    abductive_inferences: list[AbductiveInference]
    ooda_breakpoints: list[OODABreakpoint]
    toc_bottlenecks: list[TOCBottleneck]
    consistency_issues: list[ConsistencyIssue]


OODA_PATTERNS = {
    "Observe": [r"(?:采集|收集|监控|检测|感知|探针|传感器|日志|事件|告警|数据源)", r"\b(?:collect|monitor|detect|sense|observe|log|event|alert)\b"],
    "Orient": [r"(?:分析|评估|研判|关联|上下文|情境|态势|画像|建模|风险评估)", r"\b(?:analy[sz]e|assess|correlate|context|situat|model|risk)\b"],
    "Decide": [r"(?:决策|判断|规则|策略|阈值|响应方案|处置|定级|分类|优先级)", r"\b(?:decide|decision|rule|policy|threshold|response|classif|priority)\b"],
    "Act": [r"(?:执行|处置|阻断|隔离|修复|恢复|通知|报告|工单|自动化响应|编排)", r"\b(?:act|execute|block|isolate|remediate|restore|notify|report|automate|orchestrat)\b"],
}


class Step5Analysis:
    """Step 5：分析执行"""

    def __init__(self):
        self.pattern_matcher = PatternMatcher()
        self.consistency_checker = ConsistencyChecker()

    def execute(
        self, description: str,
        data_requirements_text: str = "",
    ) -> AnalysisResult:

        # 1. 溯因推理
        inferences = self._abductive_reasoning(description, data_requirements_text)

        # 2. OODA 分析
        ooda_breakpoints = self._ooda_analysis(description)

        # 3. TOC 分析
        bottlenecks = self._toc_analysis(description, data_requirements_text)

        # 4. 一致性检查
        views_data = self._prepare_views_data(data_requirements_text)
        consistency_issues = self.consistency_checker.check_views(views_data)

        return AnalysisResult(
            abductive_inferences=inferences,
            ooda_breakpoints=ooda_breakpoints,
            toc_bottlenecks=bottlenecks,
            consistency_issues=consistency_issues,
        )

    def _abductive_reasoning(
        self, description: str, data_text: str
    ) -> list[AbductiveInference]:
        """溯因推理：基于已知模式推断缺失关系"""
        inferences: list[AbductiveInference] = []

        combined_text = f"{description}\n{data_text}"
        pattern_matches = self.pattern_matcher.match_all(combined_text)

        # 检测已存在的模式
        found_patterns = {m.pattern_type for m in pattern_matches}

        # DM2 五大原子关联期望
        expected_patterns = {
            PatternType.ACTIVITY_PERFORMER: "Activity-Performer 绑定",
            PatternType.RESOURCE_FLOW: "Resource-Flow 资源流",
            PatternType.CAPABILITY_ACTIVITY: "Capability-Activity 映射",
            PatternType.WHOLE_PART: "Whole-Part 分解关系",
            PatternType.BEFORE_AFTER: "Before-After 时序关系",
            PatternType.RULE_CONSTRAINT: "Rule-Constraint 约束关系",
        }

        for pattern_type, label in expected_patterns.items():
            if pattern_type not in found_patterns:
                inferences.append(AbductiveInference(
                    entity_a="未知",
                    entity_b="未知",
                    inferred_relation=label,
                    confidence=0.45,
                    rationale=f"未检测到 {label} 模式，架构可能缺少此类关系。"
                             f"建议补充相关实体和关联。",
                ))

        # 从已匹配模式推断完整关系
        for match in pattern_matches:
            inferences.append(AbductiveInference(
                entity_a="(从描述提取)",
                entity_b="(从描述提取)",
                inferred_relation=match.description,
                confidence=match.confidence,
                rationale=f"匹配文本: {match.matched_text[:80]}",
            ))

        return inferences

    def _ooda_analysis(self, description: str) -> list[OODABreakpoint]:
        """OODA 分析：检测决策循环断点"""
        breakpoints: list[OODABreakpoint] = []

        phase_results = {}
        for phase, patterns in OODA_PATTERNS.items():
            found = False
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    found = True
                    break
            phase_results[phase] = found

        ooda_chain = ["Observe", "Orient", "Decide", "Act"]
        missing = [p for p in ooda_chain if not phase_results[p]]

        for phase in missing:
            # 找到前一个存在的阶段作为断点上下文
            prev_phase = None
            for p in reversed(ooda_chain[:ooda_chain.index(phase)]):
                if phase_results[p]:
                    prev_phase = p
                    break

            reasons = {
                "Observe": "缺少数据采集/监控环节，架构无法感知环境变化",
                "Orient": "缺少分析/评估环节，采集的数据无法转化为态势认知",
                "Decide": "缺少决策/规则引擎，分析结果无法触发响应动作",
                "Act": "缺少执行/响应环节，决策无法落地为实际操作",
            }

            breakpoints.append(OODABreakpoint(
                node=prev_phase or "入口",
                missing_phase=phase,
                reason=reasons.get(phase, f"OODA 链中缺少 {phase} 阶段"),
            ))

        return breakpoints

    def _toc_analysis(
        self, description: str, data_text: str
    ) -> list[TOCBottleneck]:
        """TOC 瓶颈分析：在资源流链路上识别瓶颈节点"""
        bottlenecks: list[TOCBottleneck] = []

        combined = f"{description}\n{data_text}"

        # 提取流节点
        flow_patterns = [
            r"(?:采集|输入|产出|输出|转发|处理|分析|存储|展示|下发|同步)"
            r"\s*(?:层|模块|组件|节点|服务|系统|引擎|平台)",
            r"(?:collector|input|output|processor|analyzer|storage|display|forward)",
        ]

        nodes = []
        for p in flow_patterns:
            matches = re.findall(p, combined, re.IGNORECASE)
            nodes.extend(matches)

        if not nodes:
            return bottlenecks

        # 估算每个节点的"流量"（基于描述中的出现次数）
        node_refs = {}
        for node in nodes:
            count = combined.lower().count(node.lower())
            node_refs[node] = count

        if len(node_refs) >= 2:
            # 找出入度最高/出度最低的节点（引用次数最多的即潜在瓶颈）
            sorted_nodes = sorted(node_refs.items(), key=lambda x: x[1], reverse=True)
            bottleneck_node, ref_count = sorted_nodes[0]

            bottlenecks.append(TOCBottleneck(
                node=bottleneck_node,
                in_degree=ref_count,
                out_degree=1,
                impact=f"'{bottleneck_node}' 在描述中被引用 {ref_count} 次，"
                       f"可能是架构中的关键约束点。如果该节点失效，整个流程可能中断。",
            ))

        return bottlenecks

    def _prepare_views_data(self, data_text: str) -> dict[str, str]:
        """将数据文本转换为一致性检查器可用的格式"""
        views_data = {}
        view_pattern = r'#+\s+(OV-\w+|SV-\w+|CV-\w+|DIV-\w+|PV-\w+|SvcV-\w+|AV-\w+|StdV-\w+)'
        parts = re.split(view_pattern, data_text)
        for i in range(1, len(parts), 2):
            vid = parts[i]
            content = parts[i + 1] if i + 1 < len(parts) else ""
            views_data[vid] = content
        return views_data

    @staticmethod
    def to_json(result: AnalysisResult) -> dict:
        """将分析结果序列化为 AI Agent 可消费的 JSON"""
        return {
            "abductive_inferences": [
                {
                    "entity_a": inf.entity_a,
                    "entity_b": inf.entity_b,
                    "inferred_relation": inf.inferred_relation,
                    "confidence": inf.confidence,
                    "rationale": inf.rationale,
                }
                for inf in result.abductive_inferences
            ],
            "ooda_breakpoints": [
                {
                    "node": bp.node,
                    "missing_phase": bp.missing_phase,
                    "reason": bp.reason,
                }
                for bp in result.ooda_breakpoints
            ],
            "toc_bottlenecks": [
                {
                    "node": bn.node,
                    "in_degree": bn.in_degree,
                    "out_degree": bn.out_degree,
                    "impact": bn.impact,
                }
                for bn in result.toc_bottlenecks
            ],
            "consistency_issues": [
                {
                    "severity": issue.severity,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                }
                for issue in result.consistency_issues
            ],
        }

    def format_output(self, result: AnalysisResult) -> str:
        # 溯因推理
        inf_lines = []
        for inf in result.abductive_inferences:
            inf_lines.append(f"### {inf.inferred_relation}")
            inf_lines.append(f"- **置信度**: {inf.confidence:.0%}")
            inf_lines.append(f"- **理由**: {inf.rationale}")
            inf_lines.append("")

        # OODA
        ooda_lines = []
        for bp in result.ooda_breakpoints:
            ooda_lines.append(f"- **{bp.node} → {bp.missing_phase}**: {bp.reason}")
        if not ooda_lines:
            ooda_lines.append("- ✅ OODA 循环完整，四个阶段均有覆盖。")

        # TOC
        toc_lines = []
        for bn in result.toc_bottlenecks:
            toc_lines.append(f"### 瓶颈节点: {bn.node}")
            toc_lines.append(f"- **入度/出度**: {bn.in_degree}/{bn.out_degree}")
            toc_lines.append(f"- **影响**: {bn.impact}")
            toc_lines.append("")
        if not toc_lines:
            toc_lines.append("- 未检测到明显的资源流瓶颈。")

        # 一致性
        cs_lines = []
        for issue in result.consistency_issues:
            sev = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "•")
            cs_lines.append(f"- {sev} **[{issue.severity}]** {issue.message}")
            if issue.suggestion:
                cs_lines.append(f"  → {issue.suggestion}")
        if not cs_lines:
            cs_lines.append("- ✅ 未检测到一致性问题。")

        return f"""# Step 5：分析执行

## 溯因推理

{chr(10).join(inf_lines) if inf_lines else '未检测到可推断的缺失关系。'}

## OODA 韧性分析

{chr(10).join(ooda_lines)}

## TOC 瓶颈分析

{chr(10).join(toc_lines)}

## 一致性检查

{chr(10).join(cs_lines)}

---
*生成时间: 由 Pipeline Step 5 自动生成*
"""
