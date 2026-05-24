"""Tushare + AKShare vendor for A-share capital-flow (主力资金) data.

Primary: Tushare (token-based, official API) — reliable, structured JSON.
Fallback: AKShare (scrapes East Money 东方财富) — free, no token needed.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ---- Tushare (primary) ------------------------------------------------------

try:
    import requests as _requests

    _requests_available = True
except ImportError:
    _requests_available = False


def _get_tushare_token() -> Optional[str]:
    """Read the Tushare API token from env or config."""
    token = os.environ.get("TUSHARE_TOKEN") or os.environ.get(
        "TRADINGAGENTS_TUSHARE_TOKEN"
    )
    if token:
        return token
    try:
        from tradingagents.dataflows.config import get_config

        return get_config().get("tushare_token")
    except Exception:
        return None


def _latest_trade_date() -> str:
    """Guess the most recent trade date, skipping weekends."""
    now = datetime.now()
    # Walk backwards until we hit a weekday
    d = now
    for _ in range(7):
        if d.weekday() < 5:  # Mon-Fri
            return d.strftime("%Y%m%d")
        d = d - timedelta(days=1)
    return now.strftime("%Y%m%d")


def _tushare_moneyflow(
    *,
    ticker: str,
    trade_date: Optional[str] = None,
) -> str:
    """Fetch major capital flow from Tushare official API.

    API doc: https://tushare.pro/document/2?doc_id=43
    """
    token = _get_tushare_token()
    if not token or not _requests_available:
        return _NOT_AVAILABLE

    # Normalise ticker to Tushare format: 600519.SH or 000001.SZ
    ts_code = ticker.upper().strip()
    if not ts_code.endswith(".SH") and not ts_code.endswith(".SZ"):
        if ts_code.startswith("6"):
            ts_code = f"{ts_code}.SH"
        elif ts_code.startswith(("0", "3")):
            ts_code = f"{ts_code}.SZ"
        elif ts_code.startswith("8") or ts_code.startswith("4"):
            ts_code = f"{ts_code}.BJ"  # Beijing exchange
        else:
            return (
                f"Cannot determine exchange suffix for ticker '{ticker}'. "
                "Use full Tushare format e.g. '600519.SH' or '000001.SZ'."
            )

    trade_date = trade_date or _latest_trade_date()

    try:
        resp = _requests.post(
            "https://api.tushare.pro",
            json={
                "api_name": "moneyflow",
                "token": token,
                "params": {"ts_code": ts_code, "trade_date": trade_date},
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.error("Tushare moneyflow request failed: %s", exc)
        return f"Tushare API request failed: {exc}"

    if data.get("code") != 0:
        return f"Tushare error (code={data.get('code')}): {data.get('msg', 'unknown')}"

    items = data.get("data", {}).get("items", [])
    fields = data.get("data", {}).get("fields", [])

    if not items:
        # Try yesterday
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        if trade_date != yesterday:
            try:
                resp2 = _requests.post(
                    "https://api.tushare.pro",
                    json={
                        "api_name": "moneyflow",
                        "token": token,
                        "params": {"ts_code": ts_code, "trade_date": yesterday},
                    },
                    timeout=15,
                )
                data2 = resp2.json()
                if data2.get("code") == 0:
                    items2 = data2.get("data", {}).get("items", [])
                    if items2:
                        items = items2
                        fields = data2.get("data", {}).get("fields", [])
            except Exception:
                pass

    if not items:
        return (
            f"No capital-flow data for {ts_code} on {trade_date}. "
            "The date may be a non-trading day or data is not yet available."
        )

    row = items[0]
    d = dict(zip(fields, row))

    # Build the markdown report
    def _money(val) -> str:
        try:
            yi = float(val) / 10000.0  # 万元 → 亿元
            return f"{yi:+.2f} 亿"
        except (ValueError, TypeError):
            return str(val)

    def _vol(val) -> str:
        try:
            lots = int(float(val))
            wan_shou = lots / 100  # 手 → 万手
            return f"{wan_shou:+,.0f} 万手"
        except (ValueError, TypeError):
            return str(val)

    # net major fund = (buy_lg + buy_elg) - (sell_lg + sell_elg) in lots/amount
    net_vol = d.get("net_mf_vol", "N/A")
    net_amt = d.get("net_mf_amount", "N/A")

    buy_lg_amt = float(d.get("buy_lg_amount", 0) or 0)
    sell_lg_amt = float(d.get("sell_lg_amount", 0) or 0)
    buy_elg_amt = float(d.get("buy_elg_amount", 0) or 0)
    sell_elg_amt = float(d.get("sell_elg_amount", 0) or 0)
    buy_md_amt = float(d.get("buy_md_amount", 0) or 0)
    sell_md_amt = float(d.get("sell_md_amount", 0) or 0)
    buy_sm_amt = float(d.get("buy_sm_amount", 0) or 0)
    sell_sm_amt = float(d.get("sell_sm_amount", 0) or 0)

    # 主力净流入 = 超大单 + 大单
    mf_buy = buy_elg_amt + buy_lg_amt
    mf_sell = sell_elg_amt + sell_lg_amt
    mf_net_yi = (mf_buy - mf_sell) / 10000.0

    # Total turnover ≈ sum of all buys
    total_flow = mf_buy + buy_md_amt + buy_sm_amt
    mf_ratio = (mf_net_yi * 10000 / total_flow * 100) if total_flow > 0 else 0

    return (
        f"## 主力资金流向 — {ts_code}\n"
        f"- 数据日期: {d.get('trade_date', trade_date)} (来源: Tushare)\n"
        f"- 主力净流入: {_money(mf_buy - mf_sell)} (占成交额 {mf_ratio:+.2f}%)\n\n"
        f"| 资金分类 | 买入 | 卖出 | 净额 |\n"
        f"|----------|------|------|------|\n"
        f"| 超大单(≥100万) | {_money(buy_elg_amt)} | {_money(sell_elg_amt)} | {_money(buy_elg_amt - sell_elg_amt)} |\n"
        f"| 大单(20-100万) | {_money(buy_lg_amt)} | {_money(sell_lg_amt)} | {_money(buy_lg_amt - sell_lg_amt)} |\n"
        f"| 中单(4-20万) | {_money(buy_md_amt)} | {_money(sell_md_amt)} | {_money(buy_md_amt - sell_md_amt)} |\n"
        f"| 小单(<4万) | {_money(buy_sm_amt)} | {_money(sell_sm_amt)} | {_money(buy_sm_amt - sell_sm_amt)} |\n\n"
        f"**解读:** 主力净流入={_money(mf_buy - mf_sell)}, "
        f"{'机构资金净流入，看多信号' if (mf_buy - mf_sell) > 0 else '机构资金净流出，看空信号'}"
        f" | Tushare net_mf_vol={net_vol}手, net_mf_amount={net_amt}万元"
    )


def _tushare_sector_flow(
    *,
    sector: str,
    trade_date: Optional[str] = None,
) -> str:
    """Fetch sector-level flow from Tushare moneyflow_hsgt or similar.

    Tushare doesn't have a direct sector moneyflow API in the free tier.
    Fall back to a helpful message suggesting AKShare or manual lookup.
    """
    return (
        f"Tushare does not provide sector-level capital flow data in the free tier. "
        f"For sector '{sector}', consider using AKShare (akshare package) "
        f"or checking East Money (东方财富) sector flow rankings directly."
    )


# ---- AKShare (fallback) -----------------------------------------------------

try:
    import akshare as _ak

    _akshare_available = True
except ImportError:
    _akshare_available = False


def _akshare_moneyflow(
    *,
    ticker: str,
    period: str = "今日",
) -> str:
    """Fetch from East Money via AKShare (fallback when Tushare unavailable)."""
    if not _akshare_available:
        return _NOT_AVAILABLE

    valid_periods = {"今日", "3日", "5日", "10日"}
    if period not in valid_periods:
        period = "今日"

    try:
        df = _ak.stock_individual_fund_flow_rank(indicator=period)
    except Exception as exc:
        logger.error("AKShare moneyflow fetch failed: %s", exc)
        return f"AKShare/East Money fetch failed: {exc}"

    if df is None or df.empty:
        return f"No capital-flow data from AKShare for period '{period}'."

    col_map = {
        "代码": None, "名称": None, "最新价": None,
        "今日涨跌幅": None, "今日主力净流入-净额": None,
        "今日主力净流入-净占比": None, "今日超大单净流入-净额": None,
        "今日大单净流入-净额": None, "今日中单净流入-净额": None,
        "今日小单净流入-净额": None,
    }
    for col in df.columns:
        for key in list(col_map):
            if col_map[key] is None and key in col:
                col_map[key] = col

    target = ticker.upper().replace("SH", "").replace("SZ", "").strip()
    code_col = col_map["代码"]
    if code_col is None:
        return "AKShare column layout changed — cannot locate 代码 column."

    row = df[df[code_col].astype(str).str.contains(target)]
    if row.empty:
        return f"No AKShare data for ticker '{ticker}' (period='{period}')."

    row = row.iloc[0]

    def _fmt(key: str) -> str:
        col = col_map.get(key)
        if col is None:
            return "N/A"
        try:
            yi = float(row[col]) / 1_0000_0000
            return f"{yi:+.2f} 亿"
        except (ValueError, TypeError):
            return str(row[col])

    return (
        f"## 主力资金流向 — AKShare/东方财富\n"
        f"- 数据周期: {period}\n"
        f"- 最新价: {_fmt('最新价').replace('+', '')}\n"
        f"- 涨跌幅: {str(row.get(col_map.get('今日涨跌幅', ''), 'N/A'))}\n\n"
        f"| 资金分类 | 净流入 |\n"
        f"|----------|--------|\n"
        f"| 主力净流入 | {_fmt('今日主力净流入-净额')} |\n"
        f"| 主力净占比 | {_fmt('今日主力净流入-净占比')} |\n"
        f"| 超大单净流入 | {_fmt('今日超大单净流入-净额')} |\n"
        f"| 大单净流入 | {_fmt('今日大单净流入-净额')} |\n"
        f"| 中单净流入 | {_fmt('今日中单净流入-净额')} |\n"
        f"| 小单净流入 | {_fmt('今日小单净流入-净额')} |\n"
    )


def _akshare_sector_flow(
    *,
    sector: str,
    period: str = "今日",
) -> str:
    """Fetch sector flow from AKShare."""
    if not _akshare_available:
        return _NOT_AVAILABLE
    try:
        df = _ak.stock_sector_fund_flow_rank(indicator=period)
    except Exception as exc:
        return f"AKShare sector flow failed: {exc}"
    if df is None or df.empty:
        return "No sector data."
    for col in df.columns:
        if "名称" in col:
            matching = df[df[col].astype(str).str.contains(sector)]
            if not matching.empty:
                return f"## 板块资金流向 — '{sector}' ({period})\n\n{matching.head(5).to_string(index=False)}"
    return f"No sector matching '{sector}'."


_NOT_AVAILABLE = (
    "Capital flow data is not available. Install `akshare` (`pip install akshare>=1.16.1`) "
    "or set `TRADINGAGENTS_TUSHARE_TOKEN` environment variable with a Tushare token "
    "to enable 主力资金 analysis."
)


# ---- Public API (called by route_to_vendor) ---------------------------------


def get_moneyflow(
    *,
    ticker: str,
    period: str = "今日",
    trade_date: Optional[str] = None,
) -> str:
    """Fetch major capital flow data — Tushare first, AKShare fallback."""
    # Prefer Tushare when a token is set
    token = _get_tushare_token()
    if token and _requests_available:
        result = _tushare_moneyflow(ticker=ticker, trade_date=trade_date)
        if not result.startswith("Tushare error") and not result.startswith(
            "Tushare API request failed"
        ):
            return result
        # Fall through to AKShare

    if _akshare_available:
        return _akshare_moneyflow(ticker=ticker, period=period)

    if not token and not _akshare_available:
        return _NOT_AVAILABLE

    return _akshare_moneyflow(ticker=ticker, period=period)


def get_sector_fund_flow(
    *,
    sector: str,
    period: str = "今日",
    trade_date: Optional[str] = None,
) -> str:
    """Fetch sector-level capital flow rankings."""
    token = _get_tushare_token()
    if token and _requests_available:
        result = _tushare_sector_flow(sector=sector, trade_date=trade_date)
        if "does not provide" not in result:
            return result

    if _akshare_available:
        return _akshare_sector_flow(sector=sector, period=period)

    return _NOT_AVAILABLE
