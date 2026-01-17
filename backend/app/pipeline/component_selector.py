"""
Component Selector Module
Deterministic component selection using Redis state.
"""
import logging
import random
from typing import List, Set, Optional
from app.models.constraints import (
    Constraints, 
    ComponentCandidate, 
    SelectionResult,
    HardConstraints,
    SoftPreferences
)
import time

logger = logging.getLogger(__name__)


# Component catalog (in production, this would come from a database)
COMPONENT_CATALOG = [
    # Hero components
    ComponentCandidate(component_id="hero_base_v1", component_type="hero", genre="base", variant="v1", tags=["hero", "full-width"]),
    ComponentCandidate(component_id="hero_minimalist_v1", component_type="hero", genre="minimalist", variant="v1", tags=["hero", "clean"]),
    ComponentCandidate(component_id="hero_neobrutalist_v1", component_type="hero", genre="neobrutalist", variant="v1", tags=["hero", "bold"]),
    ComponentCandidate(component_id="hero_glassmorphism_v1", component_type="hero", genre="glassmorphism", variant="v1", tags=["hero", "blur"]),
    ComponentCandidate(component_id="hero_loud_v1", component_type="hero", genre="loud", variant="v1", tags=["hero", "test"]),
    
    # Product Grid components
    ComponentCandidate(component_id="grid_base_v1", component_type="product-grid", genre="base", variant="v1", tags=["grid", "products"]),
    ComponentCandidate(component_id="grid_minimalist_v1", component_type="product-grid", genre="minimalist", variant="v1", tags=["grid", "clean"]),
    ComponentCandidate(component_id="grid_neobrutalist_v1", component_type="product-grid", genre="neobrutalist", variant="v1", tags=["grid", "bold"]),
    ComponentCandidate(component_id="grid_glassmorphism_v1", component_type="product-grid", genre="glassmorphism", variant="v1", tags=["grid", "blur"]),
    
    # CTA components
    ComponentCandidate(component_id="cta_base_v1", component_type="cta", genre="base", variant="v1", tags=["cta", "action"]),
    ComponentCandidate(component_id="cta_minimalist_v1", component_type="cta", genre="minimalist", variant="v1", tags=["cta", "subtle"]),
    ComponentCandidate(component_id="cta_loud_v1", component_type="cta", genre="loud", variant="v1", tags=["cta", "test", "high-contrast"]),
]


class ComponentSelector:
    """
    Selects components using deterministic logic.
    All data comes from Redis (no external I/O during selection).
    """
    
    def __init__(self, catalog: List[ComponentCandidate] = None):
        self.catalog = catalog or COMPONENT_CATALOG
    
    def select(
        self,
        constraints: Constraints,
        recently_used: Set[str] = None,
        vector_candidates: List[str] = None,
        required_types: List[str] = None
    ) -> SelectionResult:
        """
        Select components based on constraints.
        
        Args:
            constraints: Hard/soft constraints from constraint builder
            recently_used: Set of component IDs to avoid
            vector_candidates: Pre-filtered candidates from vector search (optional)
            required_types: Component types to select (e.g., ["hero", "product-grid", "cta"])
            
        Returns:
            SelectionResult with selected and exploration components
        """
        start_time = time.perf_counter()
        recently_used = recently_used or set()
        required_types = required_types or ["hero", "product-grid", "cta"]
        
        # Step 1: Filter by hard constraints
        filtered = self._apply_hard_constraints(
            self.catalog, 
            constraints.hard,
            recently_used
        )
        
        # Step 2: Score by soft preferences
        scored = self._score_by_preferences(filtered, constraints.soft)
        
        # Step 3: Select best component per type
        selected = []
        exploration = []
        
        for comp_type in required_types:
            type_candidates = [c for c in scored if c.component_type == comp_type]
            
            if not type_candidates:
                logger.warning(f"No candidates found for type: {comp_type}")
                continue
            
            # Sort by combined score (preference + semantic)
            type_candidates.sort(
                key=lambda c: c.preference_score + c.semantic_score,
                reverse=True
            )
            
            # Apply exploration budget
            if random.random() < constraints.exploration_budget:
                # Pick a "loud" or exploratory component
                loud_candidates = [c for c in type_candidates if c.genre == "loud"]
                if loud_candidates:
                    exploration.append(loud_candidates[0])
                    continue
            
            # Pick the best matching component
            selected.append(type_candidates[0])
        
        selection_time = time.perf_counter() - start_time
        logger.info(f"Component selection completed in {selection_time*1000:.2f}ms")
        
        return SelectionResult(
            selected_components=selected,
            exploration_components=exploration,
            total_candidates_considered=len(self.catalog),
            selection_timestamp=time.time()
        )
    
    def _apply_hard_constraints(
        self,
        candidates: List[ComponentCandidate],
        hard: HardConstraints,
        recently_used: Set[str]
    ) -> List[ComponentCandidate]:
        """Filter candidates by hard constraints."""
        filtered = []
        
        for candidate in candidates:
            # Skip recently used
            if candidate.component_id in recently_used:
                continue
            
            # Skip explicitly excluded
            if candidate.component_id in hard.excluded_component_ids:
                continue
            
            # Device compatibility check
            if hard.device_type == "mobile" and not candidate.supports_mobile:
                continue
            
            # All checks passed
            filtered.append(candidate)
        
        return filtered
    
    def _score_by_preferences(
        self,
        candidates: List[ComponentCandidate],
        soft: SoftPreferences
    ) -> List[ComponentCandidate]:
        """Score candidates by soft preferences."""
        scored = []
        
        for candidate in candidates:
            # Genre preference score
            genre_score = soft.genre_weights.get(candidate.genre, 0.1)
            
            # Combined preference score
            candidate.preference_score = genre_score
            scored.append(candidate)
        
        return scored


# Singleton instance
component_selector = ComponentSelector()
