from app.services.datasets import st_george as data
from app.services.datasets import materials_catalog as catalog
from app.services.calculations import (
    calculate_material_costs,
    calculate_roofing_cost,
    calculate_paint_cost,
    calculate_appliance_cost,
    calculate_permit_costs,
)
from app.models.estimate import HouseInput, FlooringZone, RoofInput, PaintInput


def dollars(value: float) -> float:
    return round(value, 2)


def generate_estimate(house_input: HouseInput):
    sqft = house_input.square_footage

    flooring_zones = house_input.flooring_zones
    if not flooring_zones:
        flooring_zones = [FlooringZone(material="vinyl_plank", sqft=sqft)]

    roof = house_input.roof
    if not roof:
        # No pitch needed — if sqft is also absent, calculate_roof_area falls back to 6/12.
        roof = RoofInput(type="gable", material="architectural_shingles")

    paint = house_input.paint
    if not paint:
        paint = PaintInput(material="standard_eggshell")

    # --- Calculations ---

    material_total, material_breakdown = calculate_material_costs(sqft, flooring_zones)

    roofing_cost, roof_area = calculate_roofing_cost(sqft, roof)
    material_breakdown["roofing"] = roofing_cost
    material_total += roofing_cost

    paint_cost, wall_area, paint_area_source = calculate_paint_cost(sqft, paint)
    material_breakdown["paint"] = paint_cost
    material_total += paint_cost

    # Apply regional multiplier only to construction materials and paint.
    # Appliances are nationally priced retail products — they don't cost
    # more based on region, so they are added after the multiplier.
    material_total *= data.REGIONAL_ADJUSTMENTS["material_cost_multiplier"]

    appliance_total, appliance_breakdown = calculate_appliance_cost(house_input.appliances)
    material_breakdown["appliances"] = appliance_total
    material_total += appliance_total

    permits_total = calculate_permit_costs(sqft)
    total_cost = material_total + permits_total

    # --- Selection strings ---

    flooring_selections = []
    for zone in flooring_zones:
        option = catalog.FLOORING[zone.material]
        zone_cost = zone.sqft * option["price_per_sqft"]
        label = zone.room if zone.room else "Unassigned"
        flooring_selections.append(
            f"{label}: {option['display_name']} (${option['price_per_sqft']}/sqft x {zone.sqft} sqft = ${dollars(zone_cost):,.2f})"
        )

    roofing_option = catalog.ROOFING[roof.material]
    if roof.sqft:
        area_source = "provided"
    elif roof.pitch is not None:
        area_source = f"calculated from {roof.pitch}/12 pitch"
    else:
        area_source = "calculated from default 6/12 pitch"

    roofing_selection = (
        f"{roof.type.capitalize()} roof — "
        f"{roofing_option['display_name']} (${roofing_option['price_per_sqft']}/sqft x {roof_area} sqft [{area_source}] = ${dollars(roofing_cost):,.2f})"
    )

    paint_option = catalog.PAINT[paint.material]
    paint_selection = (
        f"{paint_option['display_name']} (${paint_option['price_per_sqft']}/sqft x {wall_area} sqft [{paint_area_source}] = ${dollars(paint_cost):,.2f})"
    )

    appliance_selections = []
    for selection in house_input.appliances:
        option = catalog.APPLIANCES[selection.appliance]
        line_total = option["unit_price"] * selection.quantity
        appliance_selections.append(
            f"{option['display_name']} x{selection.quantity} @ ${option['unit_price']:,} each = ${dollars(line_total):,.2f}"
        )

    return {
        "materials":     dollars(material_total),
        "permits":       dollars(permits_total),
        "total_cost":    dollars(total_cost),
        "cost_per_sqft": dollars(total_cost / sqft),
        "selections": {
            "flooring":   flooring_selections,
            "roofing":    [roofing_selection],
            "paint":      [paint_selection],
            "appliances": appliance_selections,
        },
        "cost_breakdown": {
            "materials": {k: dollars(v) for k, v in material_breakdown.items()}
        }
    }
