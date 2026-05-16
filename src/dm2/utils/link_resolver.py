"""
Link Resolver - Obsidian 双链解析器
解析 [[双链]] 并映射到实际文件路径
"""

from pathlib import Path
from typing import Optional


class LinkResolver:
    """
    Obsidian 双链解析器

    将 [[双链]] 转换为实际的文件路径
    支持相对路径和绝对路径
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    def resolve(self, link: str, current_file: str = None) -> Optional[Path]:
        """
        解析双链到文件路径

        Args:
            link: 双链内容（如 "Performer" 或 "../01-Performer/Performer-Template"）
            current_file: 当前文件路径（用于相对路径解析）

        Returns:
            解析后的文件路径或 None
        """
        link = link.strip()

        # 移除锚点
        if '#' in link:
            link = link.split('#')[0]

        # 移除文件扩展名
        if link.endswith('.md'):
            link = link[:-3]

        # 尝试不同的路径模式
        search_paths = []

        if current_file:
            current_dir = Path(current_file).parent
            # 相对路径
            search_paths.append(current_dir / f"{link}.md")
            search_paths.append(current_dir / link / ".md")

        # 相对于 vault 根目录
        search_paths.extend([
            self.vault_path / f"{link}.md",
            self.vault_path / link / ".md",
        ])

        # 在 vault 中递归搜索（按文件名）
        link_name = Path(link).name
        for md_file in self.vault_path.rglob("*.md"):
            if md_file.stem == link_name or md_file.name == f"{link_name}.md":
                return md_file

        # 返回第一个命中的
        for path in search_paths:
            if path.exists():
                return path

        return None

    def resolve_all(self, links: list[str], current_file: str = None) -> dict[str, Path]:
        """
        批量解析双链

        Returns:
            {link: resolved_path}
        """
        results = {}
        for link in links:
            resolved = self.resolve(link, current_file)
            if resolved:
                results[link] = resolved
        return results

    def get_link_target_name(self, link: str) -> str:
        """获取双链的目标名称"""
        # 移除路径，只保留文件名
        name = Path(link).name
        # 移除扩展名
        if name.endswith('.md'):
            name = name[:-3]
        return name
