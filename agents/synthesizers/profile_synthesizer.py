"""
Profile Synthesizer - Combines Stability and Exploratory agent outputs
Uses 80/20 weighting to produce a vectorizable User Profile JSON
"""
import json
import re
from typing import Dict, Any, List
from shared.models.user_profile import UserProfile, VisualPreferences, InteractionPreferences, BehavioralPreferences, InferredProfile
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
        "minimalist": {"color_scheme": "light", "density": "low", "typography_weight": "light"},
        "neobrutalist": {"color_scheme": "dark", "density": "high", "typography_weight": "bold"},
        "glassmorphism": {"color_scheme": "light", "corner_radius": "pill", "density": "low"},
        "loud": {"color_scheme": "vibrant", "button_size": "large", "typography_weight": "bold"},
        "base": {"color_scheme": "light", "corner_radius": "rounded", "density": "medium"},
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
        Synthesize a User Profile from agent proposals.
        Now async to support LLM synthesis call.
        """
        # Extract modules from both proposals
        stability_modules = self._extract_modules(stability_proposal)
        exploratory_modules = self._extract_modules(exploratory_proposal)
        
        # Compute weighted genre preferences
        genre_scores = self._compute_weighted_genres(stability_modules, exploratory_modules)
        
        # Derive visual preferences from genre scores
        visual = self._derive_visual_preferences(genre_scores)
        
        # Derive interaction preferences from motor state
        interaction = self._derive_interaction_preferences(motor_state, motor_confidence)
        
        # Derive behavioral preferences from context analysis
        behavioral = self._derive_behavioral_preferences(context_analysis)
        
        # Call LLM to infer rich narrative profile
        inferred = await self._infer_profile_narrative(
            session_id=session_id,
            visual=visual,
            interaction=interaction,
            motor_state=motor_state,
            genre_scores=genre_scores,
            context_insights=context_analysis.get("insights", ""),
        )
        
        # Build the profile
        profile = UserProfile(
            visual=visual,
            interaction=interaction,
            behavioral=behavioral,
            inferred=inferred,
        )
        
        return profile.model_dump()
    
    async def _infer_profile_narrative(
        self,
        session_id: str,
        visual: VisualPreferences,
        interaction: InteractionPreferences,
        motor_state: str,
        genre_scores: Dict[str, float],
        context_insights: str = "",
    ) -> InferredProfile:
        """
        Call LLM to synthesize a rich persona from raw metrics.
        """
        prompt = f"""
        Analyze these digital body language metrics to infer the user's deep aesthetic and behavioral persona.
        
        METRICS:
        - Motor State: {motor_state} (e.g. anxious=hesitant/jittery, determined=linear/fast)
        - Interaction Style: {interaction.model_dump()}
        - Genre Affinity scores: {genre_scores}
        - Computed Visuals: {visual.model_dump()}
        - Context Insights: {context_insights}
        
        TASK:
        Synthesize a semantic profile. BE SPECIFIC and BOLD. Do not default to "Generic Light Mode User". 
        Look for contradictions (e.g. Anxious behavior but clicks "Loud" modules -> "Impulse Buyer needing guidance").
        
        OUTPUT JSON:
        {{
            "summary": "3-5 word evocative persona (e.g. 'Anxious Neobrutalist Explorer', 'Confident Minimalist Power-User')",
            "habits": ["List 2-3 specific behavioral habits inferred from motor/interaction data"],
            "visual_keywords": ["List 3-5 specific, distinct aesthetic keywords. AVOID generic terms like 'clean'. USE terms like 'Bauhaus', 'High-Contrast', 'Glassy', 'Typography-Heavy', 'Pastel-Goth', 'Cyberpunk', etc."]
        }}
        """
        
        try:
            response = await thread_manager.run_with_model(
                session_id=session_id,
                model="gemini-2.5-flash",  # Fast model for synthesis
                prompt=prompt,
            )
            
            # Robust JSON extraction using regex
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return InferredProfile(**data)
            else:
                print(f"Warning: No JSON found in synthesis response")
                raise ValueError("No JSON found")
                
        except Exception as e:
            print(f"Profile synthesis error: {e}")
            # Fallback
            return InferredProfile(
                summary=f"{interaction.decision_confidence.title()} {visual.color_scheme.title()}-Mode User",
                habits=["Analysis failed - using fallback"],
                visual_keywords=[visual.color_scheme, visual.density],
            )
    
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
    
    def _derive_visual_preferences(self, genre_scores: Dict[str, float]) -> VisualPreferences:
        """Derive visual preferences from weighted genre scores"""
        if not genre_scores:
            return VisualPreferences()
        
        dominant_genre = max(genre_scores, key=genre_scores.get)
        genre_visual = self.GENRE_TO_VISUAL.get(dominant_genre, self.GENRE_TO_VISUAL["base"])
        
        return VisualPreferences(
            color_scheme=genre_visual.get("color_scheme", "light"),
            corner_radius=genre_visual.get("corner_radius", "rounded"),
            button_size=genre_visual.get("button_size", "medium"),
            density=genre_visual.get("density", "medium"),
            typography_weight=genre_visual.get("typography_weight", "regular"),
        )
    
    def _derive_interaction_preferences(
        self,
        motor_state: str,
        motor_confidence: float,
    ) -> InteractionPreferences:
        """Derive interaction preferences from motor state"""
        # Map motor state to decision confidence
        confidence_map = {
            "determined": "high",
            "browsing": "medium",
            "idle": "medium",
            "anxious": "low",
            "jittery": "low",
        }
        
        # Map motor state to exploration tolerance
        exploration_map = {
            "determined": "low",  # Knows what they want
            "browsing": "high",   # Open to discovery
            "idle": "medium",
            "anxious": "low",     # Needs stability
            "jittery": "medium",
        }
        
        # Map motor state to scroll behavior
        scroll_map = {
            "determined": "fast",
            "browsing": "slow",
            "idle": "moderate",
            "anxious": "slow",
            "jittery": "fast",
        }
        
        return InteractionPreferences(
            decision_confidence=confidence_map.get(motor_state, "medium"),
            exploration_tolerance=exploration_map.get(motor_state, "medium"),
            scroll_behavior=scroll_map.get(motor_state, "moderate"),
        )
    
    def _derive_behavioral_preferences(
        self,
        context_analysis: Dict[str, Any],
    ) -> BehavioralPreferences:
        """Derive behavioral preferences from context analysis"""
        confidence = context_analysis.get("confidence", 0.5)
        
        if confidence > 0.7:
            speed_accuracy = "accuracy"
            depth = "deep"
        elif confidence > 0.4:
            speed_accuracy = "balanced"
            depth = "moderate"
        else:
            speed_accuracy = "speed"
            depth = "shallow"
        
        return BehavioralPreferences(
            speed_vs_accuracy=speed_accuracy,
            engagement_depth=depth,
        )


profile_synthesizer = ProfileSynthesizer()
