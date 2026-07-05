import pytest
from types import SimpleNamespace

from app.services.formatters import (
    dollars,
    format_flooring_selections,
    format_roofing_selection,
    format_paint_selection,
    format_appliance_selections,
    format_wall_selections,
)
from app.models.estimate import FlooringZone, RoofInput, PaintInput, ApplianceSelection


# ── dollars ────────────────────────────────────────────────────────────────────

class TestDollars:
    def test_rounds_to_two_decimals(self):
        assert dollars(1.576) == 1.58

    def test_whole_number(self):
        assert dollars(100) == 100.0

    def test_zero(self):
        assert dollars(0) == 0.0


# ── format_flooring_selections ─────────────────────────────────────────────────

class TestFormatFlooringSelections:
    def test_with_room_label(self):
        zones = [FlooringZone(material="vinyl_plank", sqft=500, room="Living Room")]
        result = format_flooring_selections(zones)
        assert len(result) == 1
        assert "Living Room" in result[0]
        assert "Vinyl Plank" in result[0]
        assert "500" in result[0]

    def test_without_room_label_shows_unassigned(self):
        zones = [FlooringZone(material="carpet", sqft=300)]
        result = format_flooring_selections(zones)
        assert "Unassigned" in result[0]

    def test_multiple_zones(self):
        zones = [
            FlooringZone(material="vinyl_plank", sqft=500),
            FlooringZone(material="ceramic_tile", sqft=200, room="Kitchen"),
        ]
        result = format_flooring_selections(zones)
        assert len(result) == 2
        assert "Kitchen" in result[1]

    def test_empty_zones(self):
        result = format_flooring_selections([])
        assert result == []

    def test_shows_cost(self):
        zones = [FlooringZone(material="vinyl_plank", sqft=100)]
        result = format_flooring_selections(zones)
        assert "$300.00" in result[0]


# ── format_roofing_selection ───────────────────────────────────────────────────

class TestFormatRoofingSelection:
    def test_shows_material_and_area(self):
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles")
        result = format_roofing_selection(roof, 1200, 4800.0)
        assert "Architectural Shingles" in result
        assert "1200" in result
        assert "$4,800.00" in result

    def test_area_source_calculated(self):
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles")
        result = format_roofing_selection(roof, 1200, 4800.0)
        assert "calculated from 6/12 pitch" in result

    def test_area_source_provided(self):
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles", sqft=1200)
        result = format_roofing_selection(roof, 1200, 4800.0)
        assert "provided" in result

    def test_roof_type_capitalized(self):
        roof = RoofInput(type="hip", pitch=6, material="architectural_shingles")
        result = format_roofing_selection(roof, 1000, 4000.0)
        assert "Hip" in result


# ── format_paint_selection ─────────────────────────────────────────────────────

class TestFormatPaintSelection:
    def test_shows_material_and_area(self):
        paint = PaintInput(material="standard_eggshell")
        result = format_paint_selection(paint, 3000, 1050.0, "estimated walls + ceiling")
        assert "Standard Eggshell" in result
        assert "3000" in result
        assert "$1,050.00" in result

    def test_shows_area_source(self):
        paint = PaintInput(material="basic_flat")
        result = format_paint_selection(paint, 2000, 400.0, "wall geometry + ceiling")
        assert "wall geometry + ceiling" in result

    def test_provided_area_source(self):
        paint = PaintInput(material="premium_satin")
        result = format_paint_selection(paint, 5000, 2750.0, "provided walls + ceiling")
        assert "provided walls + ceiling" in result


# ── format_appliance_selections ────────────────────────────────────────────────

class TestFormatApplianceSelections:
    def test_empty_list(self):
        result = format_appliance_selections([])
        assert result == []

    def test_single_appliance(self):
        selections = [ApplianceSelection(appliance="refrigerator_standard", quantity=1)]
        result = format_appliance_selections(selections)
        assert len(result) == 1
        assert "Refrigerator (Standard)" in result[0]
        assert "$1,200.00" in result[0]

    def test_multiple_quantity(self):
        selections = [ApplianceSelection(appliance="microwave", quantity=2)]
        result = format_appliance_selections(selections)
        assert "x2" in result[0]
        assert "$500.00" in result[0]

    def test_multiple_appliances(self):
        selections = [
            ApplianceSelection(appliance="washer", quantity=1),
            ApplianceSelection(appliance="dryer", quantity=1),
        ]
        result = format_appliance_selections(selections)
        assert len(result) == 2


# ── format_wall_selections ─────────────────────────────────────────────────────

class TestFormatWallSelections:
    def test_with_wall_result(self):
        house_input = SimpleNamespace(wall_segments=["w1", "w2"])
        wall_result = {
            "lumber_lf": 150.5,
            "drywall_sqft": 400.0,
            "sheathing_sqft": 200.0,
            "insulation_sqft": 200.0,
        }
        result = format_wall_selections(house_input, wall_result)
        assert len(result) == 1
        assert "2 wall segment(s)" in result[0]
        assert "150.5" in result[0]

    def test_without_wall_result_shows_fallback_message(self):
        house_input = SimpleNamespace(wall_segments=[])
        result = format_wall_selections(house_input, None)
        assert len(result) == 1
        assert "No wall segments provided" in result[0]
