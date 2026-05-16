"""
Pattern Matcher - DM2 常见架构模式检测

用于从自然语言描述中快速识别常见的 DM2 / DoDAF 关系模式，
为后续的 6W 分析、视图推荐和架构校验提供启发式线索。
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PatternType(str, Enum):
    """常见架构模式类型"""

    WHOLE_PART = "whole_part"
    OVERLAP = "overlap"
    SUPER_SUBTYPE = "super_subtype"
    BEFORE_AFTER = "before_after"
    ACTIVITY_PERFORMER = "activity_performer"
    CAPABILITY_ACTIVITY = "capability_activity"
    RESOURCE_FLOW = "resource_flow"
    RULE_CONSTRAINT = "rule_constraint"


@dataclass
class PatternMatch:
    """模式匹配结果"""

    pattern_type: PatternType
    description: str
    matched_text: str
    confidence: float = 0.6


class PatternMatcher:
    """基于规则的轻量模式检测器"""

    def __init__(self):
        self._patterns: list[tuple[PatternType, list[str], str, float]] = [
            (
                PatternType.WHOLE_PART,
                [
                    r"(?:由|包括|包含|组成|下辖|分为)[:：]?[^。；\n]{0,40}",
                    r"(?:consists of|includes|composed of)\s+[^.;\n]{0,40}",
                ],
                "检测到整体-部分（Whole-Part）结构，可关注分解树与组成关系。",
                0.72,
            ),
            (
                PatternType.OVERLAP,
                [
                    r"(?:共享|复用|兼任|交叉|重叠)[:：]?[^。；\n]{0,40}",
                    r"(?:shared by|overlap|shared role)\s+[^.;\n]{0,40}",
                ],
                "检测到重叠/共享（Overlap）关系，可关注多角色或多组织共享。",
                0.68,
            ),
            (
                PatternType.SUPER_SUBTYPE,
                [
                    r"(?:类型|子类|属于|细分为|分类为)[:：]?[^。；\n]{0,40}",
                    r"(?:subtype|sub-class|category|type of)\s+[^.;\n]{0,40}",
                ],
                "检测到泛化-特化（Super-Subtype）关系，可关注分类体系和能力分层。",
                0.66,
            ),
            (
                PatternType.BEFORE_AFTER,
                [
                    r"(?:先|后|之前|之后|前置|后继|触发|顺序|阶段)[:：]?[^。；\n]{0,40}",
                    r"(?:before|after|prerequisite|successor|trigger|phase)\s+[^.;\n]{0,40}",
                ],
                "检测到时序（Before-After）关系，可关注 OV-6b/OV-6c 或阶段演进。",
                0.70,
            ),
            (
                PatternType.ACTIVITY_PERFORMER,
                [
                    r"(?:由[^。；\n]{0,20}(?:执行|负责|承担))",
                    r"(?:执行者|责任方|责任单位|责任角色)[:：]?[^。；\n]{0,40}",
                    r"(?:performed by|responsible for)\s+[^.;\n]{0,40}",
                ],
                "检测到活动-执行者绑定，可关注 OV-5b、OV-4、SV-1。",
                0.81,
            ),
            (
                PatternType.CAPABILITY_ACTIVITY,
                [
                    r"(?:能力|capability)[:：]?[^。；\n]{0,20}(?:通过|支撑|映射到|对应)[^。；\n]{0,20}(?:活动|流程|任务)",
                    r"(?:活动|任务|流程)[:：]?[^。；\n]{0,20}(?:体现|支撑|实现)[^。；\n]{0,20}(?:能力|目标)",
                ],
                "检测到能力-活动映射，可关注 CV-2、CV-6、OV-5a。",
                0.84,
            ),
            (
                PatternType.RESOURCE_FLOW,
                [
                    r"(?:输入|输出|交换|传递|流向|资源流|信息流|数据流)[:：]?[^。；\n]{0,40}",
                    r"(?:input|output|exchange|flow|resource flow|data flow)\s+[^.;\n]{0,40}",
                ],
                "检测到资源/信息流，可关注 OV-2、SV-2、DIV-2/3。",
                0.80,
            ),
            (
                PatternType.RULE_CONSTRAINT,
                [
                    r"(?:依据|遵循|约束|规则|标准|规范|要求|必须|应当)[:：]?[^。；\n]{0,40}",
                    r"(?:rule|constraint|policy|standard|must|should|required)\s+[^.;\n]{0,40}",
                ],
                "检测到规则/约束，可关注 StdV-1、OV-6a 与约束传播链。",
                0.78,
            ),
        ]

    def match_all(self, text: str) -> list[PatternMatch]:
        """匹配文本中的所有已知模式并按置信度排序。"""
        if not text or not text.strip():
            return []

        matches: list[PatternMatch] = []
        seen: set[tuple[PatternType, str]] = set()

        for pattern_type, regexes, description, confidence in self._patterns:
            for regex in regexes:
                for match in re.finditer(regex, text, re.IGNORECASE):
                    matched_text = match.group(0).strip(" ：:;,.，。；\n\t")
                    key = (pattern_type, matched_text)
                    if matched_text and key not in seen:
                        seen.add(key)
                        matches.append(
                            PatternMatch(
                                pattern_type=pattern_type,
                                description=description,
                                matched_text=matched_text,
                                confidence=confidence,
                            )
                        )

        return sorted(matches, key=lambda item: item.confidence, reverse=True)

    def match_best(self, text: str) -> Optional[PatternMatch]:
        """返回最可能的模式。"""
        matches = self.match_all(text)
        return matches[0] if matches else None


__all__ = ["PatternMatcher", "PatternMatch", "PatternType"]
