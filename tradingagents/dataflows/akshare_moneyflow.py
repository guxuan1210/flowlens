"""AKShare vendor for A-share capital-flow (主力资金) data.

Powered by East Money (东方财富) via AKShare.
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    ak = None  # type: ignore


def get_moneyflow(
    *,
    ticker: str,
    period: str = "今日",
) -> str:
    """Fetch major capital flow data for *ticker* from East Money via AKShare.

    Parameters
    ----------
    ticker : str
        A-share ticker code such as "000001" (平安银行) or "600519" (贵州茅台).
    period : str, optional
        Lookback window — one of "今日", "3日", "5日", "10日" (default "今日").

    Returns
    -------
    str
        An LLM-friendly markdown summary including 主力/超大单/大单/中单/小单
        net inflow amounts, ratios, price change, and the period label.
    """
    if not AKSHARE_AVAILABLE:
        return (
            "AKShare is not installed. Install it with: "
            "`pip install akshare>=1.16.1` to enable capital-flow analysis."
        )

    valid_periods = {"今日", "3日", "5日", "10日"}
    if period not in valid_periods:
        period = "今日"

    try:
        df = ak.stock_individual_fund_flow_rank(indicator=period)
    except Exception as exc:
        logger.error("AKShare moneyflow fetch failed: %s", exc)
        return f"Failed to fetch capital-flow data for {ticker}: {exc}"

    if df is None or df.empty:
        return f"No capital-flow data returned by AKShare for period '{period}'."

    # AKShare column names (as of v1.16+) — match by substring.
    col_map: Dict[str, Optional[str]] = {
        "代码": None,
        "名称": None,
        "最新价": None,
        "今日涨跌幅": None,
        "今日主力净流入-净额": None,
        "今日主力净流入-净占比": None,
        "今日超大单净流入-净额": None,
        "今日大单净流入-净额": None,
        "今日中单净流入-净额": None,
        "今日小单净流入-净额": None,
    }
    for col in df.columns:
        for key in col_map:
            if col_map[key] is None and key in col:
                col_map[key] = col

    # Normalise ticker matching — strip exchange prefixes/suffixes.
    target = ticker.upper().replace("SH", "").replace("SZ", "").strip()
    code_col = col_map["代码"]
    if code_col is None:
        return (
            "AKShare capital-flow column layout changed — "
            "could not locate 代码 column."
        )

    row = df[df[code_col].astype(str).str.contains(target)]
    if row.empty:
        return (
            f"No capital-flow data found for ticker '{ticker}' "
            f"(period='{period}'). The ticker may be an ETF, index, or "
            "unsupported instrument."
        )

    row = row.iloc[0]

    def _fmt(key: str) -> str:
        col = col_map.get(key)
        if col is None:
            return "N/A"
        val = row[col]
        try:
            num = float(val)
            yi = num / 1_0000_0000  # 1 亿 = 1e8 CNY
            return f"{yi:+.2f} 亿"
        except (ValueError, TypeError):
            return str(val)

    name = _fmt("名称").replace("+", "").replace("-", "").strip()
    price = _fmt("最新价").replace("+", "")
    pct_chg_col = col_map.get("今日涨跌幅")
    try:
        pct_chg = f"{float(row[pct_chg_col]):+.2f}%" if pct_chg_col else "N/A"
    except (ValueError, TypeError):
        pct_chg = str(row[pct_chg_col]) if pct_chg_col else "N/A"

    return (
        f"## 主力资金流向 — {name} ({ticker})\n"
        f"- 数据周期: {period}\n"
        f"- 最新价: {price}\n"
        f"- 涨跌幅: {pct_chg}\n\n"
        f"| 资金分类 | 净流入 |\n"
        f"|----------|--------|\n"
        f"| 主力净流入 | {_fmt('今日主力净流入-净额')} |\n"
        f"| 主力净占比 | {_fmt('今日主力净流入-净占比')} |\n"
        f"| 超大单净流入 | {_fmt('今日超大单净流入-净额')} |\n"
        f"| 大单净流入 | {_fmt('今日大单净流入-净额')} |\n"
        f"| 中单净流入 | {_fmt('今日中单净流入-净额')} |\n"
        f"| 小单净流入 | {_fmt('今日小单净流入-净额')} |\n"
    )


def get_sector_fund_flow(
    *,
    sector: str,
    period: str = "今日",
) -> str:
    """Fetch sector-level capital flow rankings.

    Parameters
    ----------
    sector : str
        Sector keyword to search for (e.g. "银行", "新能源").
    period : str
        "今日", "5日", or "10日".

    Returns
    -------
    str
        Markdown summary of matching sector flows.
    """
    if not AKSHARE_AVAILABLE:
        return "AKShare is not installed."

    try:
        df = ak.stock_sector_fund_flow_rank(indicator=period)
    except Exception as exc:
        logger.error("AKShare sector flow fetch failed: %s", exc)
        return f"Failed to fetch sector flow data: {exc}"

    if df is None or df.empty:
        return "No sector fund flow data available."

    for col in df.columns:
        if "名称" in col:
            matching = df[df[col].astype(str).str.contains(sector)]
            if not matching.empty:
                top = matching.head(5).to_string(index=False)
                return f"## 板块资金流向 — 匹配 '{sector}' ({period})\n\n{top}"

    return f"No sectors matching '{sector}' found for period '{period}'."
