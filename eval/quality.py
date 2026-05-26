"""LLM-as-judge quality evaluator for agent output text."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime

from tradingagents.llm_clients import create_llm_client
from tradingagents.default_config import DEFAULT_CONFIG

DIMENSIONS = [
    "reasoning_clarity",
    "evidence_grounding",
    "rating_thesis_alignment",
    "actionability",
    "format_completeness",
]

SYSTEM_PROMPT_EN = """\
You are an expert evaluator of AI-generated trading analysis. Your job is to \
score the quality of a Portfolio Manager's final decision output.

You will receive:
- The DECISION TEXT (markdown with sections: Rating, Executive Summary, \
Investment Thesis, Price Target, Time Horizon)
- The declared RATING (Buy/Overweight/Hold/Underweight/Sell)

Score each dimension on a 1-5 scale using these anchors:
1 = Poor — critical gaps, missing sections, incoherent logic, contradictory thesis
2 = Below Average — notable omissions or weak justification
3 = Adequate — meets basic expectations but lacks depth or specificity
4 = Good — solid, specific, minor improvements possible
5 = Excellent — exceptional clarity, evidence-rich, fully actionable

Dimensions:
1. reasoning_clarity — Is the logic chain easy to follow? No leaps or \
contradictions?
2. evidence_grounding — Are claims anchored in specific data, analyst findings, \
or debate arguments? Vague generalities score low.
3. rating_thesis_alignment — Does the thesis direction match the rating? \
Bullish thesis + Sell/Underweight = inconsistency. Bearish thesis + \
Buy/Overweight = inconsistency.
4. actionability — Could a trader execute? Are entry/exit/risk parameters \
concrete? Abstract advice scores low.
5. format_completeness — Are all required sections present and well-formed? \
Missing sections or malformed markdown score low.

Return a JSON object with exactly this structure. Justifications: exactly one \
terse English sentence each. Return ONLY valid JSON, no other text.
{
  "reasoning_clarity":       {"score": <1-5>, "justification": "<one sentence>"},
  "evidence_grounding":      {"score": <1-5>, "justification": "<one sentence>"},
  "rating_thesis_alignment": {"score": <1-5>, "justification": "<one sentence>"},
  "actionability":           {"score": <1-5>, "justification": "<one sentence>"},
  "format_completeness":     {"score": <1-5>, "justification": "<one sentence>"}
}"""

SYSTEM_PROMPT_CN = """\
你是一名 AI 生成交易分析报告的专家评审员。你的工作是对投资组合经理最终决策输出的质量进行评分。

你将收到：
- 决策文本（包含 Rating/Executive Summary/Investment Thesis/Price Target/Time Horizon 的 Markdown）
- 声明的评级（Buy/Overweight/Hold/Underweight/Sell）

请对以下每个维度进行 1-5 分评分：
1 = 差 — 关键缺失、逻辑混乱、观点矛盾
2 = 低于平均 — 明显遗漏或论证薄弱
3 = 合格 — 满足基本要求但缺乏深度或具体性
4 = 良好 — 扎实、具体，仅有小幅改进空间
5 = 优秀 — 异常清晰、证据充分、完全可执行

维度：
1. reasoning_clarity — 逻辑链条是否清晰易读？有无跳跃或矛盾？
2. evidence_grounding — 论点是否有具体数据、分析师发现或辩论论据支撑？
3. rating_thesis_alignment — 投资论点方向是否与评级一致？看涨论点 + 卖出评级 = 不一致
4. actionability — 交易员能否执行？入场/退出/风险参数是否具体？
5. format_completeness — 所有必要章节是否完整且格式正确？

返回严格按以下结构的 JSON 对象，每个 justification 为一句简洁的中文。只返回有效 JSON，不要包含其他文本。
{
  "reasoning_clarity":       {"score": <1-5>, "justification": "<一句话>"},
  "evidence_grounding":      {"score": <1-5>, "justification": "<一句话>"},
  "rating_thesis_alignment": {"score": <1-5>, "justification": "<一句话>"},
  "actionability":           {"score": <1-5>, "justification": "<一句话>"},
  "format_completeness":     {"score": <1-5>, "justification": "<一句话>"}
}"""

HUMAN_TEMPLATE = """\
RATING: {rating}

DECISION TEXT:
{decision_text}"""


class QualityEvaluator:
    """Score agent decision text quality using an LLM judge."""

    def __init__(self, config: dict | None = None, scores_path: str | None = None):
        cfg = config or DEFAULT_CONFIG.copy()
        self.config = cfg
        self.language = cfg.get("output_language", "English")

        client = create_llm_client(
            provider=cfg["llm_provider"],
            model=cfg["quick_think_llm"],
            base_url=cfg.get("backend_url"),
        )
        self.llm = client.get_llm()
        self.model = cfg["quick_think_llm"]

        if scores_path:
            self.scores_path = scores_path
        else:
            self.scores_path = os.path.join(os.path.dirname(__file__), "quality_scores.json")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score_decision(
        self, ticker: str, date: str, decision_text: str, rating: str,
    ) -> dict | None:
        """Score one decision. Returns score dict or None on failure."""
        if not decision_text or not decision_text.strip():
            return None

        lang = self._detect_language(decision_text)
        system_prompt = SYSTEM_PROMPT_CN if lang == "Chinese" else SYSTEM_PROMPT_EN
        human_msg = HUMAN_TEMPLATE.format(rating=rating, decision_text=decision_text)

        try:
            raw = self.llm.invoke([
                ("system", system_prompt),
                ("human", human_msg),
            ]).content
            parsed = self._parse_response(raw)
            if parsed is None:
                return None

            overall = round(sum(parsed[d]["score"] for d in DIMENSIONS) / len(DIMENSIONS), 1)
            return {
                "ticker": ticker,
                "date": date,
                "rating": rating,
                "scored_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "model": self.model,
                "scores": parsed,
                "overall": overall,
            }
        except Exception:
            return None

    def batch_score(
        self, entries: list[dict], force: bool = False,
    ) -> dict[tuple[str, str], dict]:
        """Score resolved entries. Returns {(ticker, date): score} lookup.

        Skips already-scored entries unless force=True.
        """
        existing = {} if force else self._load_existing()
        new_scores = list(existing.values()) if not force else []

        for e in entries:
            key = (e.get("ticker", ""), e.get("date", ""))
            if key in existing and not force:
                continue

            decision_text = e.get("decision", "")
            rating = e.get("rating", "Hold")
            ticker = e.get("ticker", "")
            date = e.get("date", "")

            if not decision_text or not decision_text.strip():
                continue

            print(f"  Scoring {ticker} {date} ...")
            scored = self.score_decision(ticker, date, decision_text, rating)
            if scored:
                new_scores.append(scored)
            else:
                print(f"    -> scoring failed, skipping")

        # Rebuild lookup
        self._save_scores(new_scores)
        return {self._key(s): s for s in new_scores}

    # ------------------------------------------------------------------
    # Internal: storage
    # ------------------------------------------------------------------

    def _load_existing(self) -> dict[tuple[str, str], dict]:
        """Load quality_scores.json -> {(ticker, date): score_dict}."""
        try:
            with open(self.scores_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {self._key(s): s for s in data if self._key(s)}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_scores(self, all_scores: list[dict]) -> None:
        """Atomic write via temp file + os.replace."""
        os.makedirs(os.path.dirname(self.scores_path), exist_ok=True)
        fd, tmp = tempfile.mkstemp(
            dir=os.path.dirname(self.scores_path),
            prefix=".quality_",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(all_scores, f, ensure_ascii=False, indent=2)
            os.replace(tmp, self.scores_path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    @staticmethod
    def _key(entry: dict) -> tuple[str, str] | None:
        t = entry.get("ticker")
        d = entry.get("date")
        return (t, d) if t and d else None

    # ------------------------------------------------------------------
    # Internal: parsing
    # ------------------------------------------------------------------

    def _parse_response(self, raw: str) -> dict | None:
        """json.loads with regex fallback."""
        # Direct parse
        try:
            result = json.loads(raw)
            if all(d in result for d in DIMENSIONS):
                return {d: result[d] for d in DIMENSIONS}
        except json.JSONDecodeError:
            pass

        # Regex: extract first {...} block
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                result = json.loads(m.group())
                if all(d in result for d in DIMENSIONS):
                    return {d: result[d] for d in DIMENSIONS}
            except json.JSONDecodeError:
                pass

        return None

    # ------------------------------------------------------------------
    # Internal: language
    # ------------------------------------------------------------------

    def _detect_language(self, text: str) -> str:
        """Heuristic: >10% CJK characters -> Chinese."""
        cjk = sum(1 for ch in text if "一" <= ch <= "鿿" or "㐀" <= ch <= "䶿")
        total = len(text.replace(" ", "").replace("\n", ""))
        if total > 0 and cjk / total > 0.1:
            return "Chinese"
        return self.language
