"""Generate evaluation reports from computed metrics."""

from __future__ import annotations

import os
from datetime import datetime


def generate_report(metrics: dict, output_dir: str | None = None) -> str:
    """Generate a markdown evaluation report. Returns the report text.

    If output_dir is provided, saves the report there as a timestamped .md file.
    """
    m = metrics
    lines = []

    lines.append("# FlowLens Agent Evaluation Report")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total runs | {m['total_runs']} |")
    lines.append(f"| Resolved (returns available) | {m['resolved']} |")
    lines.append(f"| Pending (too recent) | {m['pending']} |")
    lines.append("")

    da = m["direction_accuracy"]
    lines.append(f"| **Direction accuracy** | **{da['pct']}** ({da['correct']}/{da['total']}) |")
    lines.append(f"| Avg holding return | {m['avg_raw_return']} |")
    lines.append(f"| Avg alpha vs benchmark | {m['avg_alpha']} |")
    lines.append(f"| Winners (positive return) | {m['winners']} |")
    lines.append(f"| Losers (negative return) | {m['losers']} |")
    lines.append("")

    # By Rating
    lines.append("## By Rating")
    lines.append("")
    lines.append("| Rating | Count | Win Rate | Avg Return | Avg Alpha |")
    lines.append("|--------|-------|----------|------------|-----------|")
    for rating, stats in m["by_rating"].items():
        lines.append(
            f"| **{rating}** | {stats['count']} | "
            f"{stats['win_rate'] or '—'} | {stats['avg_return'] or '—'} | "
            f"{stats['avg_alpha'] or '—'} |"
        )
    lines.append("")

    # Rating Distribution
    lines.append("### Rating Distribution")
    lines.append("")
    dist = m["rating_distribution"]
    max_count = max(dist.values()) if dist else 1
    for rating, count in dist.items():
        bar = "█" * int(count / max_count * 20) if max_count > 0 else ""
        lines.append(f"- **{rating}**: {count} {bar}")
    lines.append("")

    # Detailed Results
    lines.append("## Detailed Results")
    lines.append("")
    lines.append("| Ticker | Date | Rating | Raw Return | Alpha | Days |")
    lines.append("|--------|------|--------|-----------|-------|------|")

    # Use metrics directly rather than recomputing
    from eval.metrics import EvalMetrics
    lines.append("_[detailed results require entry-level data — use print_summary for terminal]_")
    lines.append("")

    report = "\n".join(lines)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(output_dir, f"eval_report_{ts}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to {path}")

    return report


def print_summary(metrics: dict, detailed_rows: list[dict] | None = None):
    """Print a compact console summary."""
    m = metrics
    da = m["direction_accuracy"]

    print()
    print("=" * 60)
    print("  FlowLens Eval Summary")
    print("=" * 60)
    print(f"  Total runs:     {m['total_runs']} ({m['resolved']} resolved, {m['pending']} pending)")
    print(f"  Direction acc:  {da['pct']} ({da['correct']}/{da['total']} directional calls)")
    print(f"  Avg return:     {m['avg_raw_return']}")
    print(f"  Avg alpha:      {m['avg_alpha']}")
    print(f"  Winners/Losers: {m['winners']} / {m['losers']}")
    print("-" * 60)
    print("  By Rating:")
    for rating, stats in m["by_rating"].items():
        if stats["count"] > 0:
            print(
                f"    {rating:<14s} {stats['count']:>3d} runs  "
                f"win={stats['win_rate'] or '—':>6s}  "
                f"ret={stats['avg_return'] or '—':>7s}  "
                f"alpha={stats['avg_alpha'] or '—':>7s}"
            )
    print("-" * 60)

    if detailed_rows:
        resolved_rows = [r for r in detailed_rows if not r.get("pending")]
        if resolved_rows:
            print("\n  Detailed (resolved):")
            for row in resolved_rows[:20]:  # cap at 20
                print(
                    f"    {row['ticker']:<8s} {row['date']:<12s} "
                    f"{row['rating']:<12s} ret={row['raw_return']:>8s}  "
                    f"alpha={row['alpha_return']:>8s}"
                )
            if len(resolved_rows) > 20:
                print(f"    ... and {len(resolved_rows) - 20} more")

        pending_rows = [r for r in detailed_rows if r.get("pending")]
        if pending_rows:
            print(f"\n  Pending ({len(pending_rows)}):")
            for row in pending_rows[:10]:
                print(f"    {row['ticker']:<8s} {row['date']:<12s} {row['rating']}")

    print("=" * 60)
    print()
