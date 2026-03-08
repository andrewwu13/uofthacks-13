"""
Profile Synthesizer - Combines Stability and Exploratory agent outputs
Uses 80/20 weighting to produce a vectorizable User Profile JSON
"""

import json
import re
from typing import Dict, Any, List
from shared.models.user_profile import UserProfile
from integrations.backboard.thread_manager import thread_manager


class ProfileSynthesizer:
    """
    Synthesizes outputs from Stability (80%) and Exploratory (20%) agents
    into a unified User Profile JSON for vector database querying.
    """

    STABILITY_WEIGHT = 0.8
    EXPLORATORY_WEIGHT = 0.2

    # Mapping from module genres to visual preferences
    GENRE_TO_VISUAL = {
        "minimalist": {
            "color_scheme": "light",
            "density": "low",
            "typography_weight": "light",
        },
        "neobrutalist": {
            "color_scheme": "dark",
            "density": "high",
            "typography_weight": "bold",
        },
        "glassmorphism": {
            "color_scheme": "light",
            "corner_radius": "pill",
            "density": "low",
        },
        "loud": {
            "color_scheme": "vibrant",
            "button_size": "large",
            "typography_weight": "bold",
        },
        "base": {
            "color_scheme": "light",
            "corner_radius": "rounded",
            "density": "medium",
        },
    }

    async def synthesize(
        self,
        session_id: str,
        stability_proposal: Dict[str, Any],
        exploratory_proposal: Dict[str, Any],
        motor_state: str,
        motor_confidence: float,
        context_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesize a User Profile from agent proposals and raw metrics.
        Returns a dictionary dumped from the UserProfile model.
        """
        stability_modules = self._extract_modules(stability_proposal)
        exploratory_modules = self._extract_modules(exploratory_proposal)

        genre_scores = self._compute_weighted_genres(
            stability_modules, exploratory_modules
        )

        vibe_summary = await self._generate_vibe_summary(
            session_id=session_id,
            motor_state=motor_state,
            genre_scores=genre_scores,
            context_insights=context_analysis.get("insights", ""),
        )

        profile = UserProfile(vibe_summary=vibe_summary)
        return profile.model_dump()

    async def _generate_vibe_summary(
        self,
        session_id: str,
        motor_state: str,
        genre_scores: Dict[str, float],
        context_insights: str = "",
    ) -> str:
        """
        Call LLM to synthesize a 20-30 word condensed persona summary.
        Maintains an 80/20 balance between established preferences (exploitation)
        and novelty (exploration).
        """
        prompt = f"""
        Analyze the following digital body language metrics to produce a concise, analytical profile of the user's UI/UX preferences. This output will be vectorized to match against product catalogs, so you must use clear, descriptive, industry-standard design terms rather than poetic or narrative language.
        
        METRICS:
        - Motor State: {motor_state} (e.g., anxious indicates hesitation or erratic movement; determined indicates linear, decisive paths)
        - Genre Affinity Scores: {genre_scores}
        - Context Insights: {context_insights}
        
        TASK:
        Output a single string of keywords and clear declarative phrases specifying the exact visual traits, layout density, typography style, and interaction patterns suited for this user. 
        Do NOT output JSON. Do NOT write a narrative or use poetic language. 
        
        CRITICAL CONSTRAINT:
        - Focus 80% on their established preferences based on the highest scored genres and motor state.
        - Focus 20% on a secondary, exploratory style they might tolerate or be gently tested with.
        
        EXAMPLE: "High density layouts, dark mode color schemes, bold typography, neobrutalist styling; secondary tolerance for minimalist components with high whitespace and light themes."
        """

        from agents.config import agent_config
        model = agent_config.context_analyst_model

        try:
            response = await thread_manager.run_with_model(
                session_id=session_id,
                model=model,
                prompt=prompt,
            )
            return response.strip()
        except Exception as e:
            print(f"Profile synthesis error: {e}")
            dominant_genre = max(genre_scores, key=genre_scores.get) if genre_scores else "base"
            return f"Standard user exhibiting {motor_state} behavior, leaning towards a {dominant_genre} aesthetic."

    def _extract_modules(self, proposal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all modules from a proposal"""
        modules = []
        if "add_modules" in proposal:
            modules.extend(proposal.get("add_modules", []))
        for section in proposal.get("sections", []):
            modules.extend(section.get("modules", []))
        return modules

    def _compute_weighted_genres(
        self,
        stability_modules: List[Dict[str, Any]],
        exploratory_modules: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Compute weighted genre scores from both agent outputs"""
        genre_counts: Dict[str, float] = {}

        if not stability_modules and not exploratory_modules:
            return {"base": 1.0}

        # Count stability genres (80% weight)
        for module in stability_modules:
            genre = module.get("genre", "base")
            genre_counts[genre] = genre_counts.get(genre, 0) + self.STABILITY_WEIGHT

        # Count exploratory genres (20% weight)
        for module in exploratory_modules:
            genre = module.get("genre", "base")
            genre_counts[genre] = genre_counts.get(genre, 0) + self.EXPLORATORY_WEIGHT

        # Normalize to percentages
        total = sum(genre_counts.values()) or 1
        return {genre: score / total for genre, score in genre_counts.items()}



profile_synthesizer = ProfileSynthesizer()
