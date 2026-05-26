"""Evaluation metrics for agent trading decisions."""

from __future__ import annotations

from tradingagents.agents.utils.rating import RATINGS_5_TIER


def _parse_pct(val) -> float | None:
    """Parse a percentage string like '+5.13%' into a decimal float (0.0513), or return None."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) / 100
    if isinstance(val, str):
        try:
            return float(val.strip().rstrip("%").replace("+", "")) / 100
        except (ValueError, AttributeError):
            return None
    return None


class EvalMetrics:
    """Compute performance metrics from memory log entries."""

    def __init__(self, entries: list[dict]):
        self.entries = entries
        self.resolved = [e for e in entries if not e.get("pending")]
        self.pending = [e for e in entries if e.get("pending")]
        self._bullish = {"buy", "overweight"}
        self._bearish = {"sell", "underweight"}

    def compute(self) -> dict:
        return {
            "total_runs": len(self.entries),
            "resolved": len(self.resolved),
            "pending": len(self.pending),
            "direction_accuracy": self.direction_accuracy(),
            "by_rating": self.by_rating(),
            "rating_distribution": self.rating_distribution(),
            "avg_raw_return": self.avg_holding_return(),
            "avg_alpha": self.total_alpha(),
            "winners": self._count_positive(),
            "losers": self._count_negative(),
        }

    def direction_accuracy(self) -> dict:
        """Directional accuracy: bullish -> positive return, bearish -> negative.

        Hold ratings are excluded (no directional expectation).
        """
        correct, total = 0, 0
        for e in self.resolved:
            rating = e.get("rating", "Hold").lower()
            raw = _parse_pct(e.get("raw"))
            if raw is None or rating == "hold":
                continue
            total += 1
            if (rating in self._bullish and raw > 0) or (
                rating in self._bearish and raw < 0
            ):
                correct += 1

        return {
            "correct": correct,
            "total": total,
            "pct": f"{correct / total * 100:.1f}%" if total > 0 else "N/A",
            "raw_value": correct / total if total > 0 else 0.0,
        }

    def by_rating(self) -> dict:
        """Per-rating: count, avg raw return, avg alpha, directional win rate."""
        buckets = {}
        for rating in RATINGS_5_TIER:
            entries = [e for e in self.resolved if e.get("rating") == rating]
            if not entries:
                buckets[rating] = {
                    "count": 0, "avg_return": None, "avg_alpha": None, "win_rate": None,
                }
                continue

            raws = [_parse_pct(e.get("raw")) for e in entries]
            raws = [r for r in raws if r is not None]
            alphas = [_parse_pct(e.get("alpha")) for e in entries]
            alphas = [a for a in alphas if a is not None]

            wins = 0
            total = 0
            for e in entries:
                raw = _parse_pct(e.get("raw"))
                if raw is None:
                    continue
                total += 1
                r = rating.lower()
                if (r in self._bullish and raw > 0) or (r in self._bearish and raw < 0):
                    wins += 1

            buckets[rating] = {
                "count": len(entries),
                "avg_return": f"{sum(raws) / len(raws):+.2%}" if raws else None,
                "avg_alpha": f"{sum(alphas) / len(alphas):+.2%}" if alphas else None,
                "win_rate": f"{wins / total * 100:.1f}%" if total > 0 else None,
            }
        return buckets

    def rating_distribution(self) -> dict:
        dist = {}
        for rating in RATINGS_5_TIER:
            dist[rating] = len([e for e in self.entries if e.get("rating") == rating])
        return dist

    def avg_holding_return(self) -> str:
        raws = [_parse_pct(e.get("raw")) for e in self.resolved]
        raws = [r for r in raws if r is not None]
        if not raws:
            return "N/A"
        return f"{sum(raws) / len(raws):+.2%}"

    def total_alpha(self) -> str:
        alphas = [_parse_pct(e.get("alpha")) for e in self.resolved]
        alphas = [a for a in alphas if a is not None]
        if not alphas:
            return "N/A"
        return f"{sum(alphas) / len(alphas):+.2%}"

    def _count_positive(self) -> int:
        return len([e for e in self.resolved if (_parse_pct(e.get("raw")) or 0) > 0])

    def _count_negative(self) -> int:
        return len([e for e in self.resolved if (_parse_pct(e.get("raw")) or 0) < 0])

    def detailed_results(self) -> list[dict]:
        """Return flat list of entries for tabular display."""
        rows = []
        for e in self.resolved:
            raw = _parse_pct(e.get("raw"))
            alpha = _parse_pct(e.get("alpha"))
            rows.append({
                "ticker": e.get("ticker", ""),
                "date": e.get("date", ""),
                "rating": e.get("rating", "Hold"),
                "raw_return": f"{raw:+.2%}" if raw is not None else "—",
                "alpha_return": f"{alpha:+.2%}" if alpha is not None else "—",
                "holding_days": e.get("holding", "—"),
                "pending": False,
            })
        for e in self.pending:
            rows.append({
                "ticker": e.get("ticker", ""),
                "date": e.get("date", ""),
                "rating": e.get("rating", "Hold"),
                "raw_return": "pending",
                "alpha_return": "pending",
                "holding_days": "—",
                "pending": True,
            })
        return rows
