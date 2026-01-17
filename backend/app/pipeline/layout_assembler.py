"""
Layout Assembler Module
Assembles layout schema from selected components and caches with hash.
"""
import hashlib
import json
import logging
import time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.constraints import ComponentCandidate, SelectionResult
from app.models.reducer import ReducerOutput

logger = logging.getLogger(__name__)


class LayoutComponent(BaseModel):
    """Single component in the layout schema"""
    id: str
    type: str
    variant: str
    genre: str
    props: Dict[str, Any] = Field(default_factory=dict)


class LayoutTokens(BaseModel):
    """Design tokens derived from preferences"""
    theme: str = "light"
    border_radius: str = "8px"
    font_weight: str = "400"
    density: str = "medium"
    accent_color: str = "#3b82f6"


class LayoutSchema(BaseModel):
    """
    Complete layout schema for frontend rendering.
    This is the final output of the pipeline.
    """
    layout_id: str
    layout_hash: str
    session_id: str
    timestamp: float
    components: List[LayoutComponent]
    tokens: LayoutTokens
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LayoutAssembler:
    """
    Assembles layout schema from components and preferences.
    Handles caching and hash-based change detection.
    """
    
    def assemble(
        self,
        session_id: str,
        selection: SelectionResult,
        reducer_output: ReducerOutput,
        previous_hash: Optional[str] = None
    ) -> LayoutSchema:
        """
        Assemble a layout schema from selected components.
        
        Args:
            session_id: Current session ID
            selection: Result from component selector
            reducer_output: Original reducer output for tokens
            previous_hash: Previous layout hash for change detection
            
        Returns:
            LayoutSchema ready for frontend consumption
        """
        start_time = time.perf_counter()
        
        # Build components list
        components = self._build_components(selection)
        
        # Extract design tokens from preferences
        tokens = self._extract_tokens(reducer_output)
        
        # Generate layout ID and hash
        layout_id = f"layout_{session_id}_{int(time.time())}"
        layout_hash = self._compute_hash(components, tokens)
        
        # Check if layout changed
        if previous_hash and layout_hash == previous_hash:
            logger.info(f"Layout unchanged (hash: {layout_hash[:8]}...)")
        
        schema = LayoutSchema(
            layout_id=layout_id,
            layout_hash=layout_hash,
            session_id=session_id,
            timestamp=time.time(),
            components=components,
            tokens=tokens,
            metadata={
                "exploration_count": len(selection.exploration_components),
                "total_components": len(components),
                "assembly_time_ms": (time.perf_counter() - start_time) * 1000
            }
        )
        
        logger.info(f"Layout assembled: {len(components)} components, hash: {layout_hash[:8]}...")
        return schema
    
    def _build_components(self, selection: SelectionResult) -> List[LayoutComponent]:
        """Convert selected components to layout components."""
        components = []
        
        # Add selected components
        for candidate in selection.selected_components:
            components.append(LayoutComponent(
                id=candidate.component_id,
                type=candidate.component_type,
                variant=candidate.variant,
                genre=candidate.genre,
                props=self._default_props_for_type(candidate.component_type)
            ))
        
        # Add exploration components (marked for A/B testing)
        for candidate in selection.exploration_components:
            components.append(LayoutComponent(
                id=candidate.component_id,
                type=candidate.component_type,
                variant=candidate.variant,
                genre=candidate.genre,
                props={
                    **self._default_props_for_type(candidate.component_type),
                    "_is_exploration": True,
                    "_module_loud": True
                }
            ))
        
        return components
    
    def _extract_tokens(self, reducer_output: ReducerOutput) -> LayoutTokens:
        """Extract design tokens from reducer output."""
        visual = reducer_output.visual
        
        # Map preferences to CSS values
        radius_map = {"sharp": "0px", "rounded": "8px", "pill": "9999px"}
        weight_map = {"light": "300", "regular": "400", "bold": "700"}
        theme_map = {"dark": "dark", "light": "light", "vibrant": "vibrant"}
        
        return LayoutTokens(
            theme=theme_map.get(visual.color_scheme, "light"),
            border_radius=radius_map.get(visual.corner_radius, "8px"),
            font_weight=weight_map.get(visual.typography_weight, "400"),
            density=visual.density,
            accent_color="#3b82f6"  # Could be dynamic based on preferences
        )
    
    def _default_props_for_type(self, component_type: str) -> Dict[str, Any]:
        """Get default props for a component type."""
        defaults = {
            "hero": {"title": "Welcome", "subtitle": "Discover our products"},
            "product-grid": {"columns": 4, "limit": 12},
            "cta": {"title": "Ready to get started?", "buttonText": "Shop Now"}
        }
        return defaults.get(component_type, {})
    
    def _compute_hash(self, components: List[LayoutComponent], tokens: LayoutTokens) -> str:
        """Compute a deterministic hash of the layout."""
        # Create a stable representation
        hash_data = {
            "components": [c.model_dump() for c in components],
            "tokens": tokens.model_dump()
        }
        
        # Sort keys for determinism
        json_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()


# Singleton instance
layout_assembler = LayoutAssembler()
