"""
Unit tests for the Post-Reducer DB Pipeline
"""
import pytest
import time
from datetime import datetime

from app.models.reducer import (
    ReducerOutput, 
    ReducerContext, 
    ReducerPayload,
    VisualTraits,
    InteractionTraits,
    BehavioralTraits
)
from app.models.constraints import Constraints, HardConstraints, SoftPreferences
from app.pipeline.constraint_builder import constraint_builder
from app.pipeline.component_selector import component_selector
from app.pipeline.layout_assembler import layout_assembler
from app.pipeline.redis_keys import RedisKeys, TTL


class TestConstraintBuilder:
    """Tests for constraint builder"""
    
    def test_build_constraints_default(self):
        """Test constraint building with default values"""
        output = ReducerOutput()
        context = ReducerContext(session_id="test_001")
        
        constraints = constraint_builder.build(output, context)
        
        assert isinstance(constraints, Constraints)
        assert constraints.hard.color_scheme == "light"
        assert constraints.hard.density == "medium"
        assert constraints.hard.device_type == "desktop"
        assert 0.0 <= constraints.exploration_budget <= 1.0
    
    def test_build_constraints_dark_mode(self):
        """Test constraint building with dark mode preference"""
        output = ReducerOutput(
            visual=VisualTraits(color_scheme="dark", density="low")
        )
        context = ReducerContext(session_id="test_002", device_type="mobile")
        
        constraints = constraint_builder.build(output, context)
        
        assert constraints.hard.color_scheme == "dark"
        assert constraints.hard.density == "low"
        assert constraints.hard.device_type == "mobile"
    
    def test_exploration_budget_calculation(self):
        """Test exploration budget is calculated from tolerance"""
        low_tolerance = ReducerOutput(
            interaction=InteractionTraits(exploration_tolerance="low")
        )
        high_tolerance = ReducerOutput(
            interaction=InteractionTraits(exploration_tolerance="high")
        )
        context = ReducerContext(session_id="test_003")
        
        low_constraints = constraint_builder.build(low_tolerance, context)
        high_constraints = constraint_builder.build(high_tolerance, context)
        
        assert low_constraints.exploration_budget < high_constraints.exploration_budget


class TestComponentSelector:
    """Tests for component selector"""
    
    def test_select_components(self):
        """Test basic component selection"""
        constraints = Constraints(
            hard=HardConstraints(color_scheme="light"),
            soft=SoftPreferences(),
            exploration_budget=0.0  # No exploration
        )
        
        result = component_selector.select(
            constraints=constraints,
            required_types=["hero", "product-grid"]
        )
        
        assert len(result.selected_components) >= 1
        assert result.total_candidates_considered > 0
    
    def test_recently_used_exclusion(self):
        """Test that recently used components are excluded"""
        constraints = Constraints()
        
        # First selection
        result1 = component_selector.select(constraints=constraints)
        first_hero = next(
            (c for c in result1.selected_components if c.component_type == "hero"),
            None
        )
        
        # Second selection with first hero as recently used
        if first_hero:
            result2 = component_selector.select(
                constraints=constraints,
                recently_used={first_hero.component_id}
            )
            second_heroes = [
                c for c in result2.selected_components 
                if c.component_type == "hero"
            ]
            
            # Should not contain the recently used hero
            for hero in second_heroes:
                assert hero.component_id != first_hero.component_id


class TestLayoutAssembler:
    """Tests for layout assembler"""
    
    def test_assemble_layout(self):
        """Test layout assembly"""
        constraints = Constraints()
        selection = component_selector.select(constraints=constraints)
        output = ReducerOutput()
        
        layout = layout_assembler.assemble(
            session_id="test_layout_001",
            selection=selection,
            reducer_output=output
        )
        
        assert layout.layout_id.startswith("layout_test_layout_001")
        assert len(layout.layout_hash) == 64  # SHA256 hex
        assert len(layout.components) > 0
        assert layout.tokens.theme == "light"
    
    def test_layout_hash_determinism(self):
        """Test that same inputs produce same hash"""
        constraints = Constraints(exploration_budget=0.0)  # No randomness
        selection = component_selector.select(constraints=constraints)
        output = ReducerOutput()
        
        layout1 = layout_assembler.assemble(
            session_id="test_hash",
            selection=selection,
            reducer_output=output
        )
        layout2 = layout_assembler.assemble(
            session_id="test_hash",
            selection=selection,
            reducer_output=output
        )
        
        # Hashes should be same for same inputs
        assert layout1.layout_hash == layout2.layout_hash


class TestRedisKeys:
    """Tests for Redis key schema"""
    
    def test_key_patterns(self):
        """Test key pattern generation"""
        session_id = "session_abc123"
        
        assert RedisKeys.state(session_id) == "session:session_abc123:state"
        assert RedisKeys.constraints(session_id) == "session:session_abc123:constraints"
        assert RedisKeys.layout(session_id) == "session:session_abc123:layout"
    
    def test_ttl_values(self):
        """Test TTL constants are reasonable"""
        assert TTL.SESSION == 30 * 60  # 30 minutes
        assert TTL.CANDIDATES == 5 * 60  # 5 minutes
        assert TTL.LAYOUT == 30 * 60  # 30 minutes


class TestPipelinePerformance:
    """Performance tests for critical path"""
    
    def test_constraint_builder_performance(self):
        """Constraint builder should be fast (<1ms)"""
        output = ReducerOutput()
        context = ReducerContext(session_id="perf_test")
        
        start = time.perf_counter()
        for _ in range(100):
            constraint_builder.build(output, context)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        avg_time = elapsed / 100
        assert avg_time < 1.0, f"Constraint builder too slow: {avg_time:.3f}ms"
    
    def test_component_selector_performance(self):
        """Component selection should be fast (<5ms)"""
        constraints = Constraints()
        
        start = time.perf_counter()
        for _ in range(100):
            component_selector.select(constraints=constraints)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        avg_time = elapsed / 100
        assert avg_time < 5.0, f"Component selector too slow: {avg_time:.3f}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
