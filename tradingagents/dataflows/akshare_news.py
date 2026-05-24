"""AKShare vendor for Chinese domestic financial news.

Sources: Caixin (财新), East Money (东方财富).
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


def get_global_news_akshare(
    *,
    lookback_days: int = 7,
    article_limit: int = 10,
) -> str:
    """Fetch Chinese domestic financial/macro headlines via AKShare.

    Uses Caixin (财新) as the primary source for Chinese-language macro
    and financial news. Falls back to available East Money sources.
    """
    if not _akshare_available:
        return ""

    parts: list[str] = []

    # 1. Caixin main news (财新头条)
    try:
        df = ak.stock_news_main_cx()
        if df is not None and not df.empty:
            limit = min(article_limit, len(df))
            articles = []
            for _, row in df.head(limit).iterrows():
                tag = str(row.get("tag", "")) if "tag" in df.columns else ""
                summary = str(row.get("summary", "")) if "summary" in df.columns else ""
                articles.append(f"- [{tag}] {summary}")
            if articles:
                parts.append(
                    "### 财新金融头条 (Caixin Financial Headlines)\n\n"
                    + "\n".join(articles)
                )
    except Exception as exc:
        logger.warning("AKShare Caixin news fetch failed: %s", exc)

    if not parts:
        return ""

    return (
        "## 中国国内市场新闻 (Chinese Domestic News)\n"
        "> 来源: AKShare / 财新\n\n"
        + "\n\n".join(parts)
    )


def get_news_akshare(
    *,
    ticker: str,
    article_limit: int = 20,
) -> str:
    """Fetch ticker-specific news from Chinese sources.

    Searches East Money (东方财富) for stock-specific news.
    """
    if not _akshare_available:
        return ""

    try:
        df = ak.stock_news_em(symbol=ticker.strip())
    except Exception as exc:
        logger.warning("AKShare ticker news (%s) failed: %s", ticker, exc)
        return ""

    if df is None or df.empty:
        return ""

    parts: list[str] = []
    limit = min(article_limit, len(df))
    # stock_news_em returns columns like: 标题(title), 摘要(summary), 发布时间(time), 来源(source)
    for _, row in df.head(limit).iterrows():
        title = ""
        source = ""
        time_str = ""
        url = ""
        for col in df.columns:
            col_lower = str(col).lower()
            val = str(row[col])[:200]
            if "标题" in col or "title" in col_lower:
                title = val
            elif "来源" in col or "source" in col_lower:
                source = f" ({val})" if val and val != "nan" else ""
            elif "时间" in col or "time" in col_lower or "date" in col_lower:
                time_str = f" — {val}" if val and val != "nan" else ""
            elif "url" in col_lower or "链接" in col:
                url = val if val and val != "nan" else ""

        if title:
            parts.append(f"- **{title}**{source}{time_str}")

    if not parts:
        return ""

    return (
        f"## 东方财富个股新闻 — {ticker}\n"
        f"> 来源: AKShare / 东方财富 (East Money)\n\n"
        + "\n".join(parts[:article_limit])
    )
