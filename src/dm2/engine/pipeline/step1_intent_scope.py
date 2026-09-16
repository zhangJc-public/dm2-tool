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

from dataclasses import dataclass, field

from dm2.cognitive.cynefin_analyzer import CynefinAnalyzer, Domain
from dm2.cognitive.cynefin_deriver import CynefinDeriver
from dm2.cognitive.six_w_analyzer import SIX_W_TO_DM2_GROUPS, SixW, SixWAnalyzer
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
    needs_clarification: bool = False
    scale_profile: dict = field(default_factory=dict)
    cynefin_resolution: str = "heuristic"
    cynefin_warnings: list[str] = field(default_factory=list)


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
        self.cynefin_deriver = CynefinDeriver()
        self.indexer = indexer or DM2KnowledgeIndexer()

    def execute(self, description: str) -> IntentScopeResult:
        # 1. 6W 分析
        six_w_result = self.six_w_analyzer.analyze(description)

        # 2. 生成反向质问（基于 primary + secondary 的 6W）
        questions = self._generate_clarification_questions(
            six_w_result.primary_w, six_w_result.secondary_ws
        )

        # 3. Cynefin 复杂度判定（CLI 与 pipeline 共用同一推导器）
        derivation = self.cynefin_deriver.derive(description)
        cynefin_result = self.cynefin_analyzer.assess(
            derivation.votes,
            crisis=derivation.crisis,
            scale=derivation.scale_profile,
            context=description,
            warnings=derivation.warnings,
            signal_report=derivation.signal_report,
        )

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
            needs_clarification=cynefin_result.needs_clarification,
            scale_profile={
                "systems": cynefin_result.scale_profile.systems,
                "time_span": cynefin_result.scale_profile.time_span,
                "stakeholders": cynefin_result.scale_profile.stakeholders,
            },
            cynefin_resolution=cynefin_result.resolution,
            cynefin_warnings=cynefin_result.warnings,
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
        domain: Domain,
        budget: int,
        description: str,
    ) -> str:
        max_safe_budget = 8000
        lines = [
            "## 范围边界",
            "",
            f"- **复杂度域**: {domain.value}",
            f"- **上下文预算估算**: {budget} tokens",
        ]
        if domain == Domain.DISORDER:
            lines.append(
                "- **⚠ 域判定不明**: 证据不足或跨域矛盾，视图选择前应先回答澄清问题"
            )
        if budget > max_safe_budget:
            lines.append(f"- **⚠️ 预算警告**: 估算 {budget}tokens 超过安全阈值 {max_safe_budget}tokens")
            lines.append("- **建议**: 考虑缩小范围或采用分阶段方法")
        else:
            lines.append(f"- **预算状态**: 在安全范围内（阈值 {max_safe_budget}tokens）")

        lines.append(f"- **选定数据组 ({len(data_groups)} 个):**")
        for g in data_groups:
            lines.append(f"  - {g}")
        lines.append("- **排除**: 未选中的数据组不纳入本次架构分析")
        return "\n".join(lines)

    def format_output(self, result: IntentScopeResult) -> str:
        """生成 Step 1+2 输出文档（Markdown）"""
        questions_str = "\n".join(
            f"{i}. {q}" for i, q in enumerate(result.clarification_questions, 1)
        )
        groups_str = "\n".join(f"- {g}" for g in result.selected_data_groups)
        disorder_note = (
            "\n⚠ **判定不明（Disorder）**：请优先回答上方澄清问题，暂不推荐固定视图集。"
            if result.needs_clarification else ""
        )
        warnings_str = ""
        if result.cynefin_warnings:
            warnings_str = "\n- **信号提示（启发式，未经裁定）**：\n" + "\n".join(
                f"  - ⚠ {w}" for w in result.cynefin_warnings
            )

        return f"""# Step 1+2：意图澄清 + 范围界定

## 架构意图

{result.intent_description}

## 反向质问（澄清问题）

{questions_str}

## Cynefin 复杂度评估

- **域**: {result.cynefin_domain}（{result.cynefin_resolution} ～启发式草案，未经裁定）
- **置信度**: {result.cynefin_confidence:.0%}
- **规模剖面**: 系统 {result.scale_profile.get('systems') or '?'} / 干系人 {result.scale_profile.get('stakeholders') or '?'} / 时间跨度 {result.scale_profile.get('time_span') or '未知'}（不参与域判定）
{warnings_str}
{disorder_note}

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
                "resolution": result.cynefin_resolution,
                "warnings": result.cynefin_warnings,
                "needs_clarification": result.needs_clarification,
                "scale_profile": result.scale_profile,
            },
            "six_w": {
                "primary": result.primary_w,
                "secondary": result.secondary_ws,
            },
            "selected_data_groups": result.selected_data_groups,
            "context_budget_estimate": result.context_budget_estimate,
            "scope_boundaries": result.scope_boundaries,
        }
