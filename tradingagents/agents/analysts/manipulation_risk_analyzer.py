"""Manipulation Risk Analyzer — cross-references all analyst reports
to detect institutional manipulation patterns targeting retail investors."""

from langchain_core.prompts import ChatPromptTemplate
from tradingagents.agents.utils.agent_utils import get_language_instruction


def create_manipulation_risk_analyzer(llm):

    def manipulation_risk_node(state):
        system_message = (
            "You are a Manipulation Risk Analyzer (操纵风险检测专家). "
            "Your task is to cross-reference ALL analyst reports to detect "
            "institutional manipulation patterns targeting retail investors.\n\n"
            "**Detection Framework — 5 patterns to scan:**\n\n"
            "1. **拉高出货 (Pump & Dump / Distribution Trap)**: "
            "Technical bullish + News positive + Sentiment bullish "
            "BUT 主力资金净流出 (capital flow net outflow)\n"
            "2. **打压吸筹 (Accumulation via Suppression)**: "
            "Technical bearish + News negative + Sentiment bearish "
            "BUT 主力资金净流入 (capital flow net inflow)\n"
            "3. **假突破 (False Breakout)**: "
            "Price breaks resistance / technical breakout "
            "BUT 超大单/大单 flow neutral or negative (no institutional follow-through)\n"
            "4. **估值陷阱 (Valuation Trap)**: "
            "Stock appears undervalued / fundamentals look attractive "
            "BUT 主力持续流出 (persistent institutional outflow)\n"
            "5. **情绪操控 (Sentiment Manipulation)**: "
            "Extreme retail sentiment in one direction (>80% bullish or bearish) "
            "BUT 主力 operates in the opposite direction\n\n"
            "**Output format:** Structured markdown report with these sections:\n\n"
            "1. **Overall Risk Level**: 高风险 (High) / 中风险 (Medium) / 低风险 (Low) "
            "— holistic assessment with brief justification\n"
            "2. **Detected Patterns Table**:\n"
            "   | 操纵模式 | 风险等级 | 置信度 | 证据来源 | 建议 |\n"
            "   |----------|---------|--------|---------|------|\n"
            "3. **Cross-Validation Matrix**:\n"
            "   | 维度 | 该维度方向 | 主力资金方向 | 一致性 | 说明 |\n"
            "   |------|-----------|-------------|--------|------|\n"
            "4. **Final Recommendation**: 谨慎追高 / 可考虑低吸 / 观望为主 / 建议减仓 "
            "— one clear, actionable recommendation\n\n"
            "**CRITICAL RULES:**\n"
            "- Do NOT hallucinate patterns. Only flag a pattern when there is "
            "CLEAR, SPECIFIC evidence from the reports below.\n"
            "- If capital_flow_report is empty or unavailable, state that "
            "manipulation analysis cannot be performed and set risk to 低风险 (insufficient data).\n"
            "- If no manipulation patterns are detected despite data being available, "
            "explicitly state '未检测到明显操纵信号 (No manipulation signals detected)'.\n"
            "- Confidence ratings: 高 (>80% certainty from multiple reports), "
            "中 (50-80%, partial evidence), 低 (<50%, suggestive at best).\n"
            + get_language_instruction()
        )

        reports_text = (
            f"## Market / Technical Report\n{state.get('market_report', 'N/A')}\n\n"
            f"## Sentiment Report\n{state.get('sentiment_report', 'N/A')}\n\n"
            f"## News Report\n{state.get('news_report', 'N/A')}\n\n"
            f"## Fundamentals Report\n{state.get('fundamentals_report', 'N/A')}\n\n"
            f"## Capital Flow Report\n{state.get('capital_flow_report', 'N/A')}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_message}"),
            ("human", "Analyze these reports for manipulation patterns:\n\n{reports}"),
        ])

        chain = prompt | llm
        result = chain.invoke({
            "system_message": system_message,
            "reports": reports_text,
        })

        return {"manipulation_risk_report": result.content}

    return manipulation_risk_node
