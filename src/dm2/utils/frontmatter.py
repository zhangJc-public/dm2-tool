"""
Frontmatter Parser - Obsidian YAML Frontmatter 解析器
"""

import re
from typing import Optional

import yaml


class FrontmatterParser:
    """YAML frontmatter 解析器"""

    @staticmethod
    def parse(content: str) -> Optional[dict]:
        """
        解析 Markdown 文件的 frontmatter

        Args:
            content: 文件内容

        Returns:
            frontmatter dict 或 None
        """
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None

        fm_text = match.group(1)
        try:
            return yaml.safe_load(fm_text)
        except yaml.YAMLError:
            return None

    @staticmethod
    def extract(content: str, key: str, default=None):
        """提取 frontmatter 中的特定字段"""
        fm = FrontmatterParser.parse(content)
        return fm.get(key, default) if fm else default

    @staticmethod
    def update(content: str, updates: dict) -> str:
        """
        更新 frontmatter

        Args:
            content: 原文件内容
            updates: 要更新的字段 {key: value}

        Returns:
            更新后的文件内容
        """
        fm = FrontmatterParser.parse(content)
        if fm is None:
            fm = {}

        fm.update(updates)

        new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False)
        new_frontmatter = f"---\n{new_fm}---\n"

        match = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
        if match:
            return new_frontmatter + content[match.end():]
        else:
            return new_frontmatter + content

    @staticmethod
    def extract_all_links(content: str) -> list[str]:
        """提取所有双链 [[]]"""
        return re.findall(r'\[\[([^\]]+)\]\]', content)

    @staticmethod
    def extract_tags(content: str) -> list[str]:
        """提取所有标签 #tag"""
        # 排除 frontmatter 中的 tags
        fm_match = re.match(r'^---\n.*?\n---\n(.*)$', content, re.DOTALL)
        body = fm_match.group(1) if fm_match else content

        tags = re.findall(r'#([a-zA-Z0-9_-]+)', body)
        return list(set(tags))
