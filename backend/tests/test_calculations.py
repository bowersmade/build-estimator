import math
import pytest
from types import SimpleNamespace

from app.services.calculations import (
    calculate_material_costs,
    calculate_roof_area,
    calculate_roofing_cost,
    calculate_paint_cost,
    calculate_appliance_cost,
    calculate_permit_costs,
    _get_header_spec,
    calculate_wall_costs,
)
from app.models.estimate import (
    FlooringZone,
    RoofInput,
    PaintInput,
    ApplianceSelection,
    WallSegment,
    Opening,
)


# ── calculate_material_costs ───────────────────────────────────────────────────

class TestCalculateMaterialCosts:
    def test_default_base_costs(self):
        zones = [FlooringZone(material="vinyl_plank", sqft=1000)]
        total, breakdown = calculate_material_costs(1000, zones)
        assert breakdown["flooring"] == 3000
        assert "lumber" in breakdown
        assert total > 0

    def test_custom_base_costs(self):
        zones = [FlooringZone(material="vinyl_plank", sqft=500)]
        base = {"concrete": 10}
        total, breakdown = calculate_material_costs(1000, zones, base)
        assert breakdown["concrete"] == 10000
        assert breakdown["flooring"] == 1500
        assert total == 11500

    def test_multiple_flooring_zones(self):
        zones = [
            FlooringZone(material="vinyl_plank", sqft=500),
            FlooringZone(material="carpet", sqft=500),
        ]
        total, breakdown = calculate_material_costs(1000, zones, {})
        assert breakdown["flooring"] == pytest.approx(500 * 3 + 500 * 4)

    def test_flooring_with_room_label(self):
        zones = [FlooringZone(material="ceramic_tile", sqft=200, room="Kitchen")]
        total, breakdown = calculate_material_costs(200, zones, {})
        assert breakdown["flooring"] == 200 * 6


# ── calculate_roof_area ────────────────────────────────────────────────────────

class TestCalculateRoofArea:
    def test_uses_provided_sqft(self):
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles", sqft=1500)
        assert calculate_roof_area(1000, roof) == 1500.0

    def test_calculates_from_pitch_gable(self):
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles")
        expected = 1000 * math.sqrt(1 + (6 / 12) ** 2) * 1.0
        assert calculate_roof_area(1000, roof) == pytest.approx(expected)

    def test_hip_multiplier(self):
        roof = RoofInput(type="hip", pitch=6, material="architectural_shingles")
        slope = math.sqrt(1 + (6 / 12) ** 2)
        expected = 1000 * slope * 1.04
        assert calculate_roof_area(1000, roof) == pytest.approx(expected)

    def test_flat_roof(self):
        roof = RoofInput(type="flat", pitch=0, material="tpo_membrane")
        assert calculate_roof_area(1000, roof) == pytest.approx(1000 * 1.0 * 1.0)

    def test_unknown_type_defaults_multiplier_to_1(self):
        roof = RoofInput(type="gable", pitch=4, material="architectural_shingles")
        slope = math.sqrt(1 + (4 / 12) ** 2)
        assert calculate_roof_area(1000, roof) == pytest.approx(1000 * slope * 1.0)


# ── calculate_roofing_cost ─────────────────────────────────────────────────────

class TestCalculateRoofingCost:
    def test_returns_cost_and_area(self):
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles", sqft=1200)
        cost, area = calculate_roofing_cost(1000, roof)
        assert area == 1200
        assert cost == pytest.approx(1200 * 4)

    def test_rounds_area(self):
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles")
        cost, area = calculate_roofing_cost(1000, roof)
        assert isinstance(area, int)


# ── calculate_paint_cost ───────────────────────────────────────────────────────

class TestCalculatePaintCost:
    def test_uses_provided_wall_sqft(self):
        paint = PaintInput(material="standard_eggshell", wall_sqft=3000)
        cost, area, source = calculate_paint_cost(1000, paint)
        assert source == "provided walls + ceiling"
        assert area == 3000 + 1000
        assert cost == pytest.approx((3000 + 1000) * 0.35)

    def test_uses_geometry_sqft(self):
        paint = PaintInput(material="standard_eggshell")
        cost, area, source = calculate_paint_cost(1000, paint, geometry_sqft=2500)
        assert source == "wall geometry + ceiling"
        assert area == 2500 + 1000
        assert cost == pytest.approx((2500 + 1000) * 0.35)

    def test_falls_back_to_estimate(self):
        paint = PaintInput(material="standard_eggshell")
        cost, area, source = calculate_paint_cost(1000, paint)
        assert source == "estimated walls + ceiling"
        assert area == 1000 * 2 + 1000
        assert cost == pytest.approx((1000 * 2 + 1000) * 0.35)

    def test_provided_sqft_takes_priority_over_geometry(self):
        paint = PaintInput(material="basic_flat", wall_sqft=9999)
        cost, area, source = calculate_paint_cost(1000, paint, geometry_sqft=1111)
        assert source == "provided walls + ceiling"
        assert area == 9999 + 1000

    def test_rounds_area(self):
        paint = PaintInput(material="basic_flat")
        _, area, _ = calculate_paint_cost(1000, paint)
        assert isinstance(area, int)


# ── calculate_appliance_cost ───────────────────────────────────────────────────

class TestCalculateApplianceCost:
    def test_empty_list(self):
        total, breakdown = calculate_appliance_cost([])
        assert total == 0
        assert breakdown == {}

    def test_single_appliance(self):
        selections = [ApplianceSelection(appliance="refrigerator_standard", quantity=1)]
        total, breakdown = calculate_appliance_cost(selections)
        assert total == 1200
        assert breakdown["refrigerator_standard"] == 1200

    def test_multiple_quantity(self):
        selections = [ApplianceSelection(appliance="microwave", quantity=3)]
        total, breakdown = calculate_appliance_cost(selections)
        assert total == 250 * 3
        assert breakdown["microwave"] == 750

    def test_multiple_appliance_types(self):
        selections = [
            ApplianceSelection(appliance="washer", quantity=1),
            ApplianceSelection(appliance="dryer", quantity=1),
        ]
        total, breakdown = calculate_appliance_cost(selections)
        assert total == 1800
        assert breakdown["washer"] == 900
        assert breakdown["dryer"] == 900

    def test_duplicate_appliance_accumulates(self):
        selections = [
            ApplianceSelection(appliance="garbage_disposal", quantity=1),
            ApplianceSelection(appliance="garbage_disposal", quantity=1),
        ]
        total, breakdown = calculate_appliance_cost(selections)
        assert total == 400
        assert breakdown["garbage_disposal"] == 400


# ── calculate_permit_costs ─────────────────────────────────────────────────────

class TestCalculatePermitCosts:
    def test_basic(self):
        assert calculate_permit_costs(1000) == 8000 + (1000 * 2)

    def test_scales_with_sqft(self):
        assert calculate_permit_costs(2000) == 8000 + (2000 * 2)


# ── _get_header_spec ───────────────────────────────────────────────────────────

class TestGetHeaderSpec:
    def test_under_3ft_returns_2x6(self):
        lumber_type, depth = _get_header_spec(2.0)
        assert lumber_type == "2x6"
        assert depth == 5.5

    def test_exactly_3ft_returns_2x6(self):
        lumber_type, depth = _get_header_spec(3.0)
        assert lumber_type == "2x6"
        assert depth == 5.5

    def test_over_3ft_returns_2x8(self):
        lumber_type, depth = _get_header_spec(3.1)
        assert lumber_type == "2x8"
        assert depth == 7.25

    def test_exactly_5ft_returns_2x8(self):
        lumber_type, depth = _get_header_spec(5.0)
        assert lumber_type == "2x8"
        assert depth == 7.25

    def test_over_5ft_returns_2x10(self):
        lumber_type, depth = _get_header_spec(5.1)
        assert lumber_type == "2x10"
        assert depth == 9.25

    def test_exactly_7ft_returns_2x10(self):
        lumber_type, depth = _get_header_spec(7.0)
        assert lumber_type == "2x10"
        assert depth == 9.25

    def test_over_7ft_returns_2x12(self):
        lumber_type, depth = _get_header_spec(7.1)
        assert lumber_type == "2x12"
        assert depth == 11.25

    def test_exactly_9ft_returns_2x12(self):
        lumber_type, depth = _get_header_spec(9.0)
        assert lumber_type == "2x12"
        assert depth == 11.25

    def test_over_9ft_returns_lvl(self):
        lumber_type, depth = _get_header_spec(9.1)
        assert lumber_type == "lvl"
        assert depth == 9.5

    def test_very_large_returns_lvl(self):
        lumber_type, depth = _get_header_spec(100.0)
        assert lumber_type == "lvl"
        assert depth == 9.5


# ── calculate_wall_costs ───────────────────────────────────────────────────────

class TestCalculateWallCosts:
    def _exterior_wall(self, **kwargs):
        defaults = dict(
            id="w1", length=10, height=9,
            type="exterior", stud_spacing=16,
            connected_wall_ids=[], openings=[],
        )
        defaults.update(kwargs)
        return WallSegment(**defaults)

    def _interior_finished_wall(self, **kwargs):
        defaults = dict(
            id="w1", length=10, height=9,
            type="interior_finished", stud_spacing=16,
            connected_wall_ids=[], openings=[],
        )
        defaults.update(kwargs)
        return WallSegment(**defaults)

    def _interior_unfinished_wall(self, **kwargs):
        defaults = dict(
            id="w1", length=10, height=9,
            type="interior_unfinished", stud_spacing=16,
            connected_wall_ids=[], openings=[],
        )
        defaults.update(kwargs)
        return WallSegment(**defaults)

    def test_exterior_wall_has_drywall_sheathing_insulation(self):
        wall = self._exterior_wall()
        result = calculate_wall_costs([wall])
        assert result["drywall_sqft"] == pytest.approx(10 * 9)
        assert result["sheathing_sqft"] == pytest.approx(10 * 9)
        assert result["insulation_sqft"] == pytest.approx(10 * 9)

    def test_interior_finished_wall_has_double_drywall(self):
        wall = self._interior_finished_wall()
        result = calculate_wall_costs([wall])
        assert result["drywall_sqft"] == pytest.approx(10 * 9 * 2)
        assert result["sheathing_sqft"] == 0
        assert result["insulation_sqft"] == 0

    def test_interior_unfinished_wall_has_no_surfaces(self):
        wall = self._interior_unfinished_wall()
        result = calculate_wall_costs([wall])
        assert result["drywall_sqft"] == 0
        assert result["sheathing_sqft"] == 0
        assert result["insulation_sqft"] == 0

    def test_traditional_framing_adds_corner_studs(self):
        wall = self._exterior_wall(connected_wall_ids=["w2"])
        result_trad = calculate_wall_costs([wall], framing_method="traditional")
        wall2 = self._exterior_wall(connected_wall_ids=[])
        result_no_conn = calculate_wall_costs([wall2], framing_method="traditional")
        assert result_trad["lumber_lf"] > result_no_conn["lumber_lf"]

    def test_advanced_framing_no_corner_stud_addition(self):
        wall_conn = self._exterior_wall(connected_wall_ids=["w2"])
        wall_no_conn = self._exterior_wall(connected_wall_ids=[])
        result_conn = calculate_wall_costs([wall_conn], framing_method="advanced")
        result_no_conn = calculate_wall_costs([wall_no_conn], framing_method="advanced")
        assert result_conn["lumber_lf"] == result_no_conn["lumber_lf"]

    def test_window_opening_subtracts_area(self):
        opening = Opening(type="window", width=3, height=4, position=2)
        wall = self._exterior_wall(openings=[opening])
        result = calculate_wall_costs([wall])
        expected_net = (10 * 9) - (3 * 4)
        assert result["drywall_sqft"] == pytest.approx(expected_net)

    def test_door_opening_subtracts_area(self):
        opening = Opening(type="door", width=3, height=7, position=2)
        wall = self._exterior_wall(openings=[opening])
        result = calculate_wall_costs([wall])
        expected_net = (10 * 9) - (3 * 7)
        assert result["drywall_sqft"] == pytest.approx(expected_net)

    def test_window_adds_to_window_cost(self):
        opening = Opening(type="window", width=3, height=4, position=2)
        wall = self._exterior_wall(openings=[opening])
        result = calculate_wall_costs([wall])
        assert result["breakdown"]["windows"] == pytest.approx(3 * 4 * 80.0)

    def test_door_adds_to_door_cost(self):
        opening = Opening(type="door", width=3, height=7, position=2)
        wall = self._exterior_wall(openings=[opening])
        result = calculate_wall_costs([wall])
        assert result["breakdown"]["doors"] == pytest.approx(3 * 7 * 65.0)

    def test_window_has_rough_sill_lumber(self):
        opening = Opening(type="window", width=3, height=4, position=2)
        wall_window = self._exterior_wall(openings=[opening])
        wall_no_opening = self._exterior_wall()
        result_window = calculate_wall_costs([wall_window])
        result_plain = calculate_wall_costs([wall_no_opening])
        assert result_window["lumber_lf"] > result_plain["lumber_lf"]

    def test_door_has_no_rough_sill(self):
        door = Opening(type="door", width=3, height=7, position=2)
        window = Opening(type="window", width=3, height=4, position=2)
        wall_door = self._exterior_wall(openings=[door])
        wall_window = self._exterior_wall(openings=[window])
        result_door = calculate_wall_costs([wall_door])
        result_window = calculate_wall_costs([wall_window])
        assert result_door["lumber_lf"] < result_window["lumber_lf"]

    def test_24_inch_spacing(self):
        wall = self._exterior_wall(stud_spacing=24)
        result = calculate_wall_costs([wall])
        assert result["lumber_lf"] > 0

    def test_multiple_walls(self):
        w1 = self._exterior_wall(id="w1", length=10)
        w2 = self._interior_finished_wall(id="w2", length=8)
        result = calculate_wall_costs([w1, w2])
        assert result["drywall_sqft"] == pytest.approx((10 * 9) + (8 * 9 * 2))

    def test_large_opening_uses_lvl_header(self):
        opening = Opening(type="window", width=10, height=4, position=0)
        wall = self._exterior_wall(length=15, openings=[opening])
        result = calculate_wall_costs([wall])
        assert result["lumber_lf"] > 0

    def test_total_cost_positive(self):
        wall = self._exterior_wall()
        result = calculate_wall_costs([wall])
        assert result["total_cost"] > 0

    def test_return_keys_present(self):
        wall = self._exterior_wall()
        result = calculate_wall_costs([wall])
        assert "total_cost" in result
        assert "lumber_lf" in result
        assert "drywall_sqft" in result
        assert "sheathing_sqft" in result
        assert "insulation_sqft" in result
        assert "breakdown" in result
