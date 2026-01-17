"""
Constraint Builder Module
Converts reducer JSON into hard constraints (filtering) and soft preferences (ranking).
"""
import logging
from typing import Tuple
from app.models.reducer import ReducerOutput, ReducerContext
from app.models.constraints import HardConstraints, SoftPreferences, Constraints

logger = logging.getLogger(__name__)


class ConstraintBuilder:
    """
    Builds constraints from reducer output.
    This is a deterministic, fast operation (no I/O).
    """
    
    def build(
        self, 
        reducer_output: ReducerOutput, 
        context: ReducerContext
    ) -> Constraints:
        """
        Convert reducer output into hard/soft constraints.
        
        Args:
            reducer_output: The canonical preference JSON from reducer
            context: Session context (device_type, page_type, etc.)
            
        Returns:
            Constraints object with hard and soft constraints
        """
        hard = self._build_hard_constraints(reducer_output, context)
        soft = self._build_soft_preferences(reducer_output)
        exploration_budget = self._calculate_exploration_budget(reducer_output)
        
        return Constraints(
            hard=hard,
            soft=soft,
            exploration_budget=exploration_budget
        )
    
    def _build_hard_constraints(
        self, 
        reducer_output: ReducerOutput,
        context: ReducerContext
    ) -> HardConstraints:
        """
        Extract hard constraints that components MUST satisfy.
        """
        visual = reducer_output.visual
        
        return HardConstraints(
            color_scheme=visual.color_scheme,
            density=visual.density,
            device_type=context.device_type,
            page_type=context.page_type,
            excluded_component_ids=[]  # Populated from recently_used later
        )
    
    def _build_soft_preferences(self, reducer_output: ReducerOutput) -> SoftPreferences:
        """
        Build soft preference weights for ranking.
        Higher values = stronger preference.
        """
        visual = reducer_output.visual
        interaction = reducer_output.interaction
        
        # Corner radius preferences
        corner_weights = {"sharp": 0.2, "rounded": 0.2, "pill": 0.2}
        corner_weights[visual.corner_radius] = 0.6
        
        # Typography weight preferences
        typo_weights = {"light": 0.2, "regular": 0.2, "bold": 0.2}
        typo_weights[visual.typography_weight] = 0.6
        
        # Button size preferences
        button_weights = {"small": 0.2, "medium": 0.2, "large": 0.2}
        button_weights[visual.button_size] = 0.6
        
        # Genre weights based on behavioral patterns
        genre_weights = self._infer_genre_weights(reducer_output)
        
        return SoftPreferences(
            corner_radius=corner_weights,
            typography_weight=typo_weights,
            button_size=button_weights,
            genre_weights=genre_weights
        )
    
    def _infer_genre_weights(self, reducer_output: ReducerOutput) -> dict:
        """
        Infer genre preferences from behavioral traits.
        This is a heuristic mapping.
        """
        behavioral = reducer_output.behavioral
        visual = reducer_output.visual
        
        # Start with base weights
        weights = {
            "base": 0.25,
            "minimalist": 0.25,
            "neobrutalist": 0.15,
            "glassmorphism": 0.20,
            "loud": 0.15
        }
        
        # Adjust based on density preference
        if visual.density == "low":
            weights["minimalist"] += 0.15
            weights["neobrutalist"] -= 0.10
        elif visual.density == "high":
            weights["neobrutalist"] += 0.10
            weights["minimalist"] -= 0.10
        
        # Adjust based on engagement depth
        if behavioral.engagement_depth == "shallow":
            weights["minimalist"] += 0.10
            weights["glassmorphism"] -= 0.05
        elif behavioral.engagement_depth == "deep":
            weights["glassmorphism"] += 0.10
            weights["loud"] += 0.05
        
        # Normalize to sum to 1.0
        total = sum(weights.values())
        return {k: round(v / total, 3) for k, v in weights.items()}
    
    def _calculate_exploration_budget(self, reducer_output: ReducerOutput) -> float:
        """
        Calculate exploration budget based on user's tolerance.
        Higher tolerance = more "loud" test components.
        """
        interaction = reducer_output.interaction
        
        tolerance_map = {
            "low": 0.1,
            "medium": 0.25,
            "high": 0.4
        }
        
        return tolerance_map.get(interaction.exploration_tolerance, 0.25)


# Singleton instance
constraint_builder = ConstraintBuilder()
