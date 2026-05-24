"""Capital Flow Analyst — analyzes 主力资金流向 to assess smart-money sentiment."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_capital_flow,
    get_sector_flow,
    get_language_instruction,
)


def create_capital_flow_analyst(llm):

    def capital_flow_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        asset_type = state.get("asset_type", "stock")
        instrument_context = build_instrument_context(ticker, asset_type)

        tools = [get_capital_flow, get_sector_flow]

        system_message = (
            "You are a Capital Flow Analyst specializing in 主力资金流向 "
            "(major capital flow) analysis for Chinese A-share markets.\n\n"
            "**Your task:**\n"
            "1. Call `get_capital_flow` with the target ticker to obtain "
            "major capital inflow/outflow data broken down by order size "
            "(超大单/大单/中单/小单).\n"
            "2. If relevant, call `get_sector_flow` to compare the stock's "
            "sector against broader industry flows.\n"
            "3. Interpret the data:\n"
            "   - Positive 主力净流入 suggests institutional accumulation "
            "(bullish signal).\n"
            "   - Negative 主力净流入 suggests institutional distribution "
            "(bearish signal).\n"
            "   - Compare 超大单 vs 大单 vs 小单 — a divergence between "
            "institutional (超大单/大单) and retail (小单) flows can signal "
            "smart-money positioning.\n"
            "   - Check 主力净占比 — a high ratio (>10%) indicates strong "
            "institutional conviction; a low or negative ratio suggests "
            "weak conviction or active selling.\n"
            "4. Present your findings as a structured markdown report "
            "with specific, actionable conclusions about institutional "
            "sentiment and potential short-term price impact.\n\n"
            "**Output format:** Provide a detailed report covering:\n"
            "- Summary of capital flows by order size\n"
            "- Institutional vs retail flow divergence analysis\n"
            "- Sector comparison (if available)\n"
            "- Overall assessment: 主力流入 (bullish) / 主力流出 (bearish) / 中性 (neutral)\n"
            "- A markdown table summarizing key metrics at the end.\n"
            "**IMPORTANT:** Since capital flow data is only available for "
            "Chinese A-shares, if `get_capital_flow` returns no data or an "
            "error message, clearly state that in your report and do NOT "
            "hallucinate data. Instead, note that capital flow analysis is "
            "not applicable for this ticker and suggest it may be a non-A-share "
            "instrument.\n"
            "\n"
            "**操纵模式识别 (Manipulation Pattern Recognition):**\n"
            "After your standard flow analysis, scan for these manipulation patterns:\n"
            "- **超大单/小单背离**: 超大单卖出 + 小单买入 → institutions distributing to retail (出货信号)\n"
            "- **主力净占比异常**: >20% or <-15% → unusually strong institutional activity\n"
            "- **连续多日流向趋势**: 5+ days consistent → reliable; sudden flip → potential manipulation\n"
            "- **板块联动检查**: Sector inflow but stock outflow → underperformance signal\n"
            "Add a '**操纵风险信号 (Manipulation Risk Signals)**' section with:\n"
            "  | 检测模式 | 信号值 | 风险等级 | 说明 |\n"
            "  |----------|--------|---------|------|\n"
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable,"
                    " prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    "For your reference, the current date is {current_date}. {instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "capital_flow_report": report,
        }

    return capital_flow_analyst_node
