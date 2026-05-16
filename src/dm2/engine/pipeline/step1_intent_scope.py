from __future__ import annotations
"""
Step 1+2: Intent Clarification + Scope Definition (意图澄清 + 范围界定)

融合流程:
  1. 接收用户架构描述
  2. 生成反向质问（基于 6W 维度的预定义模板）
  3. Cynefin 复杂度判定
  4. 上下文预算估算
  5. DM2 数据组选择
  6. 输出范围定义文档
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from dm2.cognitive.six_w_analyzer import SixWAnalyzer, SixW, SIX_W_TO_DM2_GROUPS
from dm2.cognitive.cynefin_analyzer import CynefinAnalyzer, CynefinDomain
from dm2.kernel.indexer import DM2KnowledgeIndexer


@dataclass
class IntentScopeResult:
    intent_description: str
    clarification_questions: list[str]
    cynefin_domain: str
    cynefin_confidence: float
    cynefin_details: str
    selected_data_groups: list[str]
    context_budget_estimate: int
    scope_boundaries: str
    primary_w: str
    secondary_ws: list[str]


REVERSE_QUESTION_TEMPLATES = {
    SixW.WHAT: [
        "当前描述中提到的'系统'或'数据'具体指什么？请明确核心实体类型（如：IDS探针、SIEM平台、资产数据库等）。",
        "架构的最终交付物是什么？是安全报表、实时告警、还是合规证据链？",
    ],
    SixW.HOW: [
        "核心活动流程是什么？例如：检测→分析→响应→复盘？各环节的输入输出是什么？",
        "是否存在自动化/人工混合的决策节点？如果有，边界在哪里？",
    ],
    SixW.WHERE: [
        "架构的物理/网络边界在哪里？是单机房、多云、还是混合（本地+云）？",
        "数据/服务部署的地理位置是否有合规限制（如数据不出境）？",
    ],
    SixW.WHO: [
        "涉及哪些组织/角色？谁负责运营、谁负责决策、谁提供技术支撑？",
        "不同角色之间的协作关系是怎样的？是否存在跨组织的数据共享？",
    ],
    SixW.WHEN: [
        "架构描述的是当前状态（as-is）还是目标状态（to-be）？时间跨度多长？",
        "是否存在阶段性里程碑？如一期建设核心检测能力，二期扩展响应自动化？",
    ],
    SixW.WHY: [
        "驱动这个架构的根本原因是什么？是合规要求（等保/密评）、业务需求、还是安全事件驱动？",
        "架构成功的衡量标准是什么？例如：MTTD < 5分钟、误报率 < 5%？",
    ],
}

DM2_GROUP_TOKEN_ESTIMATES = {
    "00-基础模式": 2000,
    "01-Performer": 3000,
    "02-Activity": 4000,
    "03-Capability": 3000,
    "04-Resource": 3500,
    "05-Guidance": 2500,
    "06-Measure": 2000,
    "07-Location": 1500,
    "08-Services": 3000,
    "09-Project": 2500,
    "10-Rules": 3000,
    "11-ResourceFlow": 3500,
    "12-Pedigree": 1500,
    "13-InformationPedigree": 1500,
    "14-OrganizationalStructure": 2000,
    "15-ReificationLevels": 1500,
    "16-InformationAndData": 4000,
}


class Step1IntentScope:
    """Step 1+2：意图澄清 + 范围界定"""

    def __init__(self, indexer: DM2KnowledgeIndexer = None):
        self.six_w_analyzer = SixWAnalyzer()
        self.cynefin_analyzer = CynefinAnalyzer()
        self.indexer = indexer or DM2KnowledgeIndexer()

    def execute(self, description: str) -> IntentScopeResult:
        # 1. 6W 分析
        six_w_result = self.six_w_analyzer.analyze(description)

        # 2. 生成反向质问（基于 primary + secondary 的 6W）
        questions = self._generate_clarification_questions(
            six_w_result.primary_w, six_w_result.secondary_ws
        )

        # 3. Cynefin 复杂度判定
        cynefin_values = self._infer_cynefin_values(description, six_w_result)
        cynefin_result = self.cynefin_analyzer.assess(cynefin_values, context=description)

        # 4. 选择 DM2 数据组
        data_groups = self._select_data_groups(six_w_result.primary_w, six_w_result.secondary_ws)

        # 5. 上下文预算估算
        budget = self._estimate_context_budget(data_groups, len(description))

        # 6. 范围边界描述
        boundaries = self._describe_boundaries(
            data_groups, cynefin_result.domain, budget, description
        )

        return IntentScopeResult(
            intent_description=description,
            clarification_questions=questions,
            cynefin_domain=cynefin_result.domain_label,
            cynefin_confidence=cynefin_result.confidence,
            cynefin_details=cynefin_result.reasoning_details,
            selected_data_groups=data_groups,
            context_budget_estimate=budget,
            scope_boundaries=boundaries,
            primary_w=six_w_result.primary_w.value,
            secondary_ws=[w.value for w in six_w_result.secondary_ws],
        )

    def _generate_clarification_questions(
        self, primary: SixW, secondary: list[SixW]
    ) -> list[str]:
        questions = []
        all_ws = [primary] + list(secondary)

        for w in all_ws[:3]:
            templates = REVERSE_QUESTION_TEMPLATES.get(w, [])
            if templates:
                questions.append(templates[0])

        if len(questions) < 2:
            questions.append(REVERSE_QUESTION_TEMPLATES[SixW.WHY][0])

        return questions

    def _infer_cynefin_values(self, description: str, six_w) -> dict[str, str]:
        """从描述推断 Cynefin 维度值"""

        system_count = "medium"
        sys_patterns = [r"(?:系统|平台|组件|模块|服务|探针|网关|防火墙|IDS|IPS|SIEM|SOC|WAF|HIDS|EDR)", r"\b(?:system|platform|component|service)\b"]
        sys_count = 0
        for p in sys_patterns:
            sys_count += len(re.findall(p, description, re.IGNORECASE))
        if sys_count <= 1:
            system_count = "simple"
        elif sys_count <= 5:
            system_count = "medium"
        else:
            system_count = "complex"

        uncertainty = "medium"
        if re.search(r"(?:不确定|未知|待定|TBD|可能|或许|大概)", description):
            uncertainty = "complex"
        if re.search(r"(?:明确|确定|已知|固定)", description):
            uncertainty = "simple"

        stakeholders = "medium"
        org_count = len(re.findall(r"(?:组织|部门|机构|团队|公司|厂商|甲方|乙方|SOC|NOC|运维|开发|安全|合规)", description))
        if org_count <= 1:
            stakeholders = "simple"
        elif org_count >= 4:
            stakeholders = "complex"

        rules = "medium"
        if re.search(r"(?:等保|密评|关基|合规|GDPR|ISO|NIST|等级保护|分级保护|2\.0|3\.0)", description):
            rules = "complex"
        if re.search(r"(?:无合规|不要求|灵活|自主)", description):
            rules = "simple"

        return {
            "system_count": system_count,
            "time_span": "medium",
            "stakeholders": stakeholders,
            "uncertainty": uncertainty,
            "rule_complexity": rules,
        }

    def _select_data_groups(self, primary: SixW, secondary: list[SixW]) -> list[str]:
        groups = set()
        groups.update(SIX_W_TO_DM2_GROUPS.get(primary, []))
        for w in secondary[:2]:
            groups.update(SIX_W_TO_DM2_GROUPS.get(w, []))
        return sorted(groups)

    def _estimate_context_budget(self, data_groups: list[str], description_len: int) -> int:
        base = 2000
        for g in data_groups:
            base += DM2_GROUP_TOKEN_ESTIMATES.get(g, 2500)
        base += description_len // 4
        return base

    def _describe_boundaries(
        self,
        data_groups: list[str],
        domain: CynefinDomain,
        budget: int,
        description: str,
    ) -> str:
        max_safe_budget = 8000
        lines = [
            f"## 范围边界",
            f"",
            f"- **复杂度域**: {domain.value}",
            f"- **上下文预算估算**: {budget} tokens",
        ]
        if budget > max_safe_budget:
            lines.append(f"- **⚠️ 预算警告**: 估算 {budget}tokens 超过安全阈值 {max_safe_budget}tokens")
            lines.append(f"- **建议**: 考虑缩小范围或采用分阶段方法")
        else:
            lines.append(f"- **预算状态**: 在安全范围内（阈值 {max_safe_budget}tokens）")

        lines.append(f"- **选定数据组 ({len(data_groups)} 个):**")
        for g in data_groups:
            lines.append(f"  - {g}")
        lines.append(f"- **排除**: 未选中的数据组不纳入本次架构分析")
        return "\n".join(lines)

    def format_output(self, result: IntentScopeResult) -> str:
        """生成 Step 1+2 输出文档（Markdown）"""
        questions_str = "\n".join(
            f"{i}. {q}" for i, q in enumerate(result.clarification_questions, 1)
        )
        groups_str = "\n".join(f"- {g}" for g in result.selected_data_groups)

        return f"""# Step 1+2：意图澄清 + 范围界定

## 架构意图

{result.intent_description}

## 反向质问（澄清问题）

{questions_str}

## Cynefin 复杂度评估

- **域**: {result.cynefin_domain}
- **置信度**: {result.cynefin_confidence:.0%}

### 评估详情

{result.cynefin_details}

## 6W 分析焦点

- **主要 6W**: {result.primary_w}
- **次要 6W**: {", ".join(result.secondary_ws) if result.secondary_ws else "无"}

## 选定 DM2 数据组

{groups_str}

## 上下文预算

- **估算 Token 消耗**: {result.context_budget_estimate}

{result.scope_boundaries}

---
*生成时间: 由 Pipeline Step 1+2 自动生成*
"""

    @staticmethod
    def to_json(result: IntentScopeResult) -> dict:
        """将结果序列化为 AI Agent 可消费的 JSON"""
        return {
            "intent_description": result.intent_description,
            "clarification_questions": result.clarification_questions,
            "cynefin": {
                "domain": result.cynefin_domain,
                "confidence": result.cynefin_confidence,
                "details": result.cynefin_details,
            },
            "six_w": {
                "primary": result.primary_w,
                "secondary": result.secondary_ws,
            },
            "selected_data_groups": result.selected_data_groups,
            "context_budget_estimate": result.context_budget_estimate,
            "scope_boundaries": result.scope_boundaries,
        }
