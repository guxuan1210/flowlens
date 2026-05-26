"""East Money (东方财富) vendor for Chinese financial news.

Uses AKShare as the underlying data bridge to access East Money's news API.
"""

from __future__ import annotations

import logging
from typing import Optional

from .config import get_config

logger = logging.getLogger(__name__)

try:
    import akshare as ak

    _akshare_available = True
except ImportError:
    _akshare_available = False
    ak = None


def get_news_eastmoney(
    ticker: str,
    start_date: str = "",
    end_date: str = "",
) -> str:
    """Fetch ticker-specific news from East Money (东方财富).

    Uses ``ak.stock_news_em`` which returns individual stock news articles
    published on East Money's platform (eastmoney.com / 东方财富网).

    Args:
        ticker: Stock ticker (e.g. "600519" for 贵州茅台, "000001" for 平安银行).
        start_date: Start date (yyyy-mm-dd), optional — not used by source.
        end_date: End date (yyyy-mm-dd), optional — not used by source.

    Returns:
        Formatted markdown string of news articles.
    """
    if not _akshare_available:
        return ""

    article_limit = get_config().get("news_article_limit", 20)

    try:
        df = ak.stock_news_em(symbol=ticker.strip())
    except Exception as exc:
        logger.warning("East Money ticker news (%s) failed: %s", ticker, exc)
        return ""

    if df is None or df.empty:
        return f"No East Money news found for {ticker}"

    parts: list[str] = []
    limit = min(article_limit, len(df))
    for _, row in df.head(limit).iterrows():
        title = ""
        source = ""
        time_str = ""
        for col in df.columns:
            col_lower = str(col).lower()
            val = str(row[col])[:300]
            if "标题" in col or "title" in col_lower:
                title = val
            elif "来源" in col or "source" in col_lower:
                source = f" ({val})" if val and val != "nan" else ""
            elif "时间" in col or "time" in col_lower or "date" in col_lower:
                time_str = f" — {val}" if val and val != "nan" else ""

        if title:
            parts.append(f"- **{title}**{source}{time_str}")

    if not parts:
        return f"No East Money news found for {ticker}"

    return (
        f"## {ticker} 东方财富个股新闻 (East Money Stock News)\n"
        f"> 来源: 东方财富网 (eastmoney.com)\n\n"
        + "\n".join(parts)
    )


def get_global_news_eastmoney(
    curr_date: str = "",
    look_back_days: Optional[int] = None,
    limit: Optional[int] = None,
) -> str:
    """Fetch Chinese macro/financial headlines from East Money (东方财富).

    Uses Caixin (财新) headlines via AKShare as primary, supplemented by
    East Money market headlines when available.

    Args:
        curr_date: Current date (yyyy-mm-dd), optional.
        look_back_days: Lookback days. Falls back to config.
        limit: Max articles. Falls back to config.

    Returns:
        Formatted markdown string of Chinese domestic news.
    """
    if not _akshare_available:
        return ""

    config = get_config()
    if look_back_days is None:
        look_back_days = config.get("global_news_lookback_days", 7)
    if limit is None:
        limit = config.get("global_news_article_limit", 10)

    parts: list[str] = []

    # 1. Caixin financial headlines (财新金融头条)
    try:
        df = ak.stock_news_main_cx()
        if df is not None and not df.empty:
            n = min(limit, len(df))
            articles = []
            for _, row in df.head(n).iterrows():
                tag = str(row.get("tag", "")) if "tag" in df.columns else ""
                summary = str(row.get("summary", "")) if "summary" in df.columns else ""
                if summary:
                    prefix = f"[{tag}] " if tag and tag != "nan" else ""
                    articles.append(f"- {prefix}{summary}")
            if articles:
                parts.append(
                    "### 财新金融头条 (Caixin)\n\n" + "\n".join(articles)
                )
    except Exception as exc:
        logger.warning("EastMoney/Caixin news fetch failed: %s", exc)

    if not parts:
        return ""

    return (
        "## 中国国内市场新闻 (Chinese Domestic News)\n"
        "> 来源: 东方财富网 / 财新 (East Money / Caixin)\n\n"
        + "\n\n".join(parts)
    )
