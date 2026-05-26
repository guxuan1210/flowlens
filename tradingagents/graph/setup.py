# TradingAgents/graph/setup.py

from typing import Any, Dict, List
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt

from tradingagents.agents import *
from tradingagents.agents.utils.agent_states import AgentState

from .analyst_execution import build_analyst_execution_plan
from .conditional_logic import ConditionalLogic


def _human_review_research(state: AgentState) -> Dict[str, Any]:
    """Pause after Research Manager so a human can review the debate synthesis."""
    payload = {
        "review_point": "research_manager",
        "ticker": state.get("company_of_interest", ""),
        "investment_plan": state.get("investment_plan", ""),
        "debate_history": state.get("investment_debate_state", {}).get("history", ""),
    }
    result = interrupt(payload)
    if result and isinstance(result, dict) and result.get("feedback"):
        current_plan = state.get("investment_plan", "")
        return {"investment_plan": current_plan + "\n\n---\n### \U0001f9d1 Human Review Feedback\n" + result["feedback"]}
    return {}


def _human_review_portfolio(state: AgentState) -> Dict[str, Any]:
    """Pause after Portfolio Manager so a human can review the final decision."""
    payload = {
        "review_point": "portfolio_manager",
        "ticker": state.get("company_of_interest", ""),
        "final_decision": state.get("final_trade_decision", ""),
        "investment_plan": state.get("investment_plan", ""),
        "trader_plan": state.get("trader_investment_plan", ""),
        "risk_debate": state.get("risk_debate_state", {}).get("history", ""),
        "past_context": state.get("past_context", ""),
    }
    result = interrupt(payload)
    if result and isinstance(result, dict) and result.get("feedback"):
        current_decision = state.get("final_trade_decision", "")
        return {"final_trade_decision": current_decision + "\n\n---\n### \U0001f9d1 Human Review Feedback\n" + result["feedback"]}
    return {}


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm: Any,
        deep_thinking_llm: Any,
        tool_nodes: Dict[str, ToolNode],
        conditional_logic: ConditionalLogic,
        analyst_concurrency_limit: int = 1,
    ):
        """Initialize with required components."""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.tool_nodes = tool_nodes
        self.conditional_logic = conditional_logic
        self.analyst_concurrency_limit = analyst_concurrency_limit

    def setup_graph(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        enable_human_review: bool = False,
        human_review_points: List[str] = None,
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "social": Social media analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
        """
        plan = build_analyst_execution_plan(
            selected_analysts,
            concurrency_limit=self.analyst_concurrency_limit,
        )

        analyst_factories = {
            "market": lambda: create_market_analyst(self.quick_thinking_llm),
            "social": lambda: create_sentiment_analyst(self.quick_thinking_llm),
            "news": lambda: create_news_analyst(self.quick_thinking_llm),
            "fundamentals": lambda: create_fundamentals_analyst(self.quick_thinking_llm),
            "capital_flow": lambda: create_capital_flow_analyst(self.quick_thinking_llm),
        }

        # Create researcher and manager nodes
        bull_researcher_node = create_bull_researcher(self.quick_thinking_llm)
        bear_researcher_node = create_bear_researcher(self.quick_thinking_llm)
        research_manager_node = create_research_manager(self.deep_thinking_llm)
        trader_node = create_trader(self.quick_thinking_llm)

        # Create risk analysis nodes
        aggressive_analyst = create_aggressive_debator(self.quick_thinking_llm)
        neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
        conservative_analyst = create_conservative_debator(self.quick_thinking_llm)
        portfolio_manager_node = create_portfolio_manager(self.deep_thinking_llm)
        manipulation_risk_node = create_manipulation_risk_analyzer(self.deep_thinking_llm)

        # Create workflow
        workflow = StateGraph(AgentState)

        # Add analyst nodes to the graph
        for spec in plan.specs:
            workflow.add_node(spec.agent_node, analyst_factories[spec.key]())
            workflow.add_node(spec.clear_node, create_msg_delete())
            workflow.add_node(spec.tool_node, self.tool_nodes[spec.key])

        # Add other nodes
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Aggressive Analyst", aggressive_analyst)
        workflow.add_node("Neutral Analyst", neutral_analyst)
        workflow.add_node("Conservative Analyst", conservative_analyst)
        workflow.add_node("Portfolio Manager", portfolio_manager_node)
        workflow.add_node("Manipulation Risk Analyzer", manipulation_risk_node)

        # Define edges
        # Start with the first analyst
        workflow.add_edge(START, plan.specs[0].agent_node)

        # Connect analysts in sequence
        for i, spec in enumerate(plan.specs):
            current_analyst = spec.agent_node
            current_tools = spec.tool_node
            current_clear = spec.clear_node

            # Add conditional edges for current analyst
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{spec.key}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)

            # Connect to next analyst or to Bull Researcher if this is the last analyst
            if i < len(plan.specs) - 1:
                workflow.add_edge(current_clear, plan.specs[i + 1].agent_node)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        # Add remaining edges
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )
        # Insert human review gate after Research Manager (before Trader)
        if enable_human_review and human_review_points and "research_manager" in human_review_points:
            workflow.add_node("Human Review Research", _human_review_research)
            workflow.add_edge("Research Manager", "Human Review Research")
            workflow.add_edge("Human Review Research", "Trader")
        else:
            workflow.add_edge("Research Manager", "Trader")

        workflow.add_edge("Trader", "Aggressive Analyst")
        workflow.add_conditional_edges(
            "Aggressive Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Conservative Analyst": "Conservative Analyst",
                "Portfolio Manager": "Portfolio Manager",
            },
        )
        workflow.add_conditional_edges(
            "Conservative Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",
                "Portfolio Manager": "Portfolio Manager",
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Aggressive Analyst": "Aggressive Analyst",
                "Portfolio Manager": "Portfolio Manager",
            },
        )

        # Insert human review gate after Portfolio Manager (before Manipulation Risk Analyzer)
        if enable_human_review and human_review_points and "portfolio_manager" in human_review_points:
            workflow.add_node("Human Review Portfolio", _human_review_portfolio)
            workflow.add_edge("Portfolio Manager", "Human Review Portfolio")
            workflow.add_edge("Human Review Portfolio", "Manipulation Risk Analyzer")
        else:
            workflow.add_edge("Portfolio Manager", "Manipulation Risk Analyzer")
        workflow.add_edge("Manipulation Risk Analyzer", END)

        return workflow
