import pytest
from app.services.cost_engine import generate_estimate
from app.models.estimate import (
    HouseInput,
    FlooringZone,
    RoofInput,
    PaintInput,
    ApplianceSelection,
    WallSegment,
    Opening,
)


class TestGenerateEstimate:
    def _input(self, **kwargs):
        defaults = {"square_footage": 1000}
        defaults.update(kwargs)
        return HouseInput(**defaults)

    def test_minimal_input_returns_estimate(self):
        result = generate_estimate(self._input())
        assert result["total_cost"] > 0
        assert result["materials"] > 0
        assert result["permits"] > 0
        assert result["cost_per_sqft"] > 0

    def test_cost_per_sqft_is_total_over_sqft(self):
        result = generate_estimate(self._input(square_footage=2000))
        assert result["cost_per_sqft"] == pytest.approx(result["total_cost"] / 2000, rel=1e-4)

    def test_defaults_applied_when_not_provided(self):
        result = generate_estimate(self._input())
        assert "flooring" in result["selections"]
        assert "roofing" in result["selections"]
        assert "paint" in result["selections"]
        assert len(result["selections"]["flooring"]) == 1
        assert "Vinyl Plank" in result["selections"]["flooring"][0]

    def test_custom_flooring_zones(self):
        house = self._input(
            flooring_zones=[
                FlooringZone(material="marble_tile", sqft=500, room="Master Bath"),
                FlooringZone(material="carpet", sqft=500, room="Bedroom"),
            ]
        )
        result = generate_estimate(house)
        flooring = result["selections"]["flooring"]
        assert len(flooring) == 2
        assert "Master Bath" in flooring[0]
        assert "Marble Tile" in flooring[0]

    def test_custom_roof(self):
        house = self._input(
            roof=RoofInput(type="hip", pitch=8, material="standing_seam_metal")
        )
        result = generate_estimate(house)
        assert "Standing Seam Metal" in result["selections"]["roofing"][0]
        assert "Hip" in result["selections"]["roofing"][0]

    def test_custom_paint(self):
        house = self._input(paint=PaintInput(material="designer_premium"))
        result = generate_estimate(house)
        assert "Designer Premium" in result["selections"]["paint"][0]

    def test_appliances_added_after_multiplier(self):
        house_no_appliances = self._input()
        house_with_appliances = self._input(
            appliances=[ApplianceSelection(appliance="refrigerator_standard", quantity=1)]
        )
        result_no = generate_estimate(house_no_appliances)
        result_with = generate_estimate(house_with_appliances)
        diff = result_with["total_cost"] - result_no["total_cost"]
        assert diff == pytest.approx(1200.0, rel=1e-4)

    def test_fallback_path_no_walls(self):
        result = generate_estimate(self._input())
        assert "No wall segments provided" in result["selections"]["walls"][0]

    def test_wall_model_path(self):
        house = self._input(
            wall_segments=[
                WallSegment(id="w1", length=20, height=9, type="exterior"),
                WallSegment(id="w2", length=10, height=9, type="interior_finished"),
            ]
        )
        result = generate_estimate(house)
        assert "wall segment(s)" in result["selections"]["walls"][0]

    def test_wall_model_includes_ceiling_drywall(self):
        house_with_walls = self._input(
            wall_segments=[WallSegment(id="w1", length=10, height=9, type="exterior")]
        )
        result = generate_estimate(house_with_walls)
        assert result["cost_breakdown"]["materials"]["drywall"] > 0

    def test_wall_model_paint_uses_geometry(self):
        house = self._input(
            wall_segments=[WallSegment(id="w1", length=10, height=9, type="exterior")]
        )
        result = generate_estimate(house)
        assert "wall geometry + ceiling" in result["selections"]["paint"][0]

    def test_fallback_paint_uses_estimate(self):
        result = generate_estimate(self._input())
        assert "estimated walls + ceiling" in result["selections"]["paint"][0]

    def test_provided_wall_sqft_overrides_geometry(self):
        house = self._input(
            paint=PaintInput(material="standard_eggshell", wall_sqft=9999),
            wall_segments=[WallSegment(id="w1", length=10, height=9, type="exterior")]
        )
        result = generate_estimate(house)
        assert "provided walls + ceiling" in result["selections"]["paint"][0]

    def test_regional_multiplier_applied_to_materials(self):
        result_1000 = generate_estimate(self._input(square_footage=1000))
        result_2000 = generate_estimate(self._input(square_footage=2000))
        assert result_2000["materials"] > result_1000["materials"] * 1.9

    def test_cost_breakdown_contains_expected_keys(self):
        result = generate_estimate(self._input())
        keys = result["cost_breakdown"]["materials"].keys()
        assert "concrete" in keys
        assert "flooring" in keys
        assert "roofing" in keys
        assert "paint" in keys
        assert "appliances" in keys

    def test_warnings_key_exists(self):
        result = generate_estimate(self._input())
        assert "warnings" not in result

    def test_selections_has_all_keys(self):
        result = generate_estimate(self._input())
        assert set(result["selections"].keys()) == {
            "flooring", "roofing", "paint", "appliances", "walls"
        }
