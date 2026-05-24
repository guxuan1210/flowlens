"""Capital-flow tools — exposes 主力资金流向 data as LLM-callable tools."""

from __future__ import annotations

from langchain_core.tools import tool

from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_capital_flow(
    ticker: str,
    period: str = "今日",
) -> str:
    """Fetch major capital flow data (主力资金流向) for a Chinese A-share stock.

    This tool queries East Money (东方财富) via AKShare and returns the net
    inflow/outflow broken down by order size: 超大单 (super-large, ≥100万CNY),
    大单 (large, 20-100万CNY), 中单 (medium, 4-20万CNY), and 小单 (small,
    <4万CNY). 主力净流入 = 超大单 + 大单.

    Use this tool to understand where institutional ("smart") money is flowing.

    Parameters
    ----------
    ticker : str
        A-share ticker code such as "000001" (平安银行) or "600519" (贵州茅台).
        Plain digits only — exchange prefixes like SH/SZ are stripped internally.
    period : str, optional
        Lookback period: "今日" (today), "3日", "5日", or "10日" (default "今日").

    Returns
    -------
    str
        Markdown table with net inflow amounts (亿元) for each order-size
        category, plus the major-flow ratio (% of turnover) and price change.
    """
    return route_to_vendor("get_capital_flow", ticker=ticker, period=period)


@tool
def get_sector_flow(
    sector: str,
    period: str = "今日",
) -> str:
    """Fetch sector-level capital flow rankings from East Money.

    Useful for comparing the target stock's sector against broader industry
    money flows. Returns the top-5 matching sectors with their net inflow data.

    Parameters
    ----------
    sector : str
        Sector name keyword, e.g. "银行", "新能源", "半导体".
    period : str
        "今日", "5日", or "10日".

    Returns
    -------
    str
        Sector capital-flow ranking table (top 5 matches).
    """
    return route_to_vendor("get_sector_flow", sector=sector, period=period)
