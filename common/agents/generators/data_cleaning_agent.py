"""
Data Cleaning Agent - Phase 1
Converts raw telemetry and interaction events into a structured, objective fact list.
Injects semantic module descriptions for any modules the user interacted with.
"""

import os
from typing import Dict, Any, List
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
from agents.concurrency_manager import llm_concurrency_manager


def _build_module_context(interactions: List[Dict[str, Any]]) -> str:
    """
    Look up module semantic descriptions for every unique (genre, layout)
    pair found in the interaction events. Returns a formatted context block
    for injection into the data cleaner prompt.

    Falls back gracefully if module_vectors is unavailable.
    """
    try:
        from app.vector.module_vectors import DESCRIPTIONS, TAGS

        # Collect unique (genre, layout) pairs from interaction metadata
        seen: set = set()
        context_lines: list = []

        for event in interactions:
            meta = event.get("metadata") or {}
            genre = meta.get("module_genre")
            layout = meta.get("module_type")  # data-module-type maps to layout slot

            if not genre or not layout:
                continue

            key = (genre, layout)
            if key in seen:
                continue
            seen.add(key)

            # DESCRIPTIONS is a nested dict: DESCRIPTIONS[genre][layout]
            genre_descs = DESCRIPTIONS.get(genre, {})
            description = genre_descs.get(layout)

            if description:
                tags = TAGS.get(genre, [])
                tag_str = ", ".join(tags[:5]) if tags else "n/a"
                # Truncate description to 80 chars for prompt efficiency
                desc_snippet = description[:80].rstrip() + "..."
                context_lines.append(
                    f'  [{genre}/{layout}] tags: {tag_str} | desc: "{desc_snippet}"'
                )

        if not context_lines:
            return "  (no matching module descriptions found)"

        return "\n".join(context_lines)

    except ImportError:
        return "  (module_vectors unavailable — context not injected)"
    except Exception as e:
        return f"  (module context lookup failed: {e})"


def _compute_event_stats(interactions: List[Dict[str, Any]]) -> str:
    """
    Pre-compute genre tallies, click counts, and loud events in Python.
    This verified tally is injected into the prompt so the small LLM
    does not need to count events itself.
    """
    from collections import Counter
    genre_counts: Counter = Counter()
    click_count = 0
    rage_click_count = 0
    loud_count = 0
    hover_total_ms = 0

    for event in interactions:
        meta = event.get("metadata") or {}
        genre = meta.get("module_genre")
        if genre:
            genre_counts[genre] += 1

        etype = event.get("type", "")
        if etype in ("click", "click_rage"):
            click_count += 1
        if etype == "click_rage":
            rage_click_count += 1
        if meta.get("is_loud"):
            loud_count += 1
        dur = event.get("duration_ms") or 0
        if dur:
            hover_total_ms += dur

    lines = [f"Total events: {len(interactions)}"]
    for genre, count in genre_counts.most_common():
        lines.append(f"  {genre}: {count} events")
    lines.append(f"Clicks: {click_count}  Rage-clicks: {rage_click_count}  Loud-module interactions: {loud_count}")
    lines.append(f"Total hover time recorded: {hover_total_ms}ms")
    return "\n".join(lines)


class DataCleaningAgent:
    """
    Phase 1 Agent: Converts raw telemetry and events into a structured,
    objective fact list with module context injected.
    Uses strict 1-agent concurrency.
    """

    def __init__(self):
        self.model = agent_config.context_analyst_model

        # Load prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "data_cleaner.txt")
        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    async def clean(
        self,
        session_id: str,
        motor_state: str,
        metrics: Dict[str, Any],
        interactions: List[Dict[str, Any]]
    ) -> str:
        """
        Run the cleaning LLM call with enriched module context.

        Args:
            session_id: Current session identifier
            motor_state: State label from StateClassifier (e.g. "dwell_focused")
            metrics: Human-readable summary dict from StateClassifier.build_motor_summary()
            interactions: Full list of TelemetryEvent dicts from the frontend

        Returns:
            Structured, objective fact-list string (no prose, no interpretation)
        """
        # Build the module context block by looking up descriptions for
        # every genre/layout pair the user actually touched
        module_context = _build_module_context(interactions)

        # Pre-compute genre tallies in Python — avoids LLM miscounting
        verified_tally = _compute_event_stats(interactions)

        prompt = self.system_prompt.format(
            motor_state=motor_state,
            metrics=metrics,
            interactions=interactions,
            module_context=module_context,
            verified_tally=verified_tally,
        )

        async with llm_concurrency_manager:
            try:
                print(f"[DataCleaningAgent] Running cleaning for {session_id}...")
                response = await thread_manager.run_with_model(
                    session_id=session_id,
                    model=self.model,
                    prompt=prompt
                )
                print(f"[DataCleaningAgent] Response: {response[:120]}...")
                return response.strip()
            except Exception as e:
                print(f"[DataCleaningAgent] Error: {e}")
                # Fallback: minimal factual summary without LLM
                event_count = len(interactions)
                genres = list({
                    (e.get("metadata") or {}).get("module_genre", "unknown")
                    for e in interactions
                    if (e.get("metadata") or {}).get("module_genre")
                })
                return (
                    f"Motor state: {motor_state}. "
                    f"{event_count} interaction events recorded. "
                    f"Genres touched: {', '.join(genres) if genres else 'unknown'}."
                )


data_cleaning_agent = DataCleaningAgent()
