import logging

from app.services.datasets import st_george as data
from app.services.datasets import materials_catalog as catalog
from app.services.calculations import (
    calculate_material_costs,
    calculate_roofing_cost,
    calculate_paint_cost,
    calculate_appliance_cost,
    calculate_permit_costs,
    calculate_wall_costs,
)
from app.services.formatters import (
    dollars,
    format_flooring_selections,
    format_roofing_selection,
    format_paint_selection,
    format_appliance_selections,
    format_wall_selections,
)
from app.models.estimate import HouseInput, FlooringZone, RoofInput, PaintInput

log = logging.getLogger(__name__)


def generate_estimate(house_input: HouseInput):
    sqft      = house_input.square_footage
    has_walls = bool(house_input.wall_segments)

    log.info(f"═══ generate_estimate | sqft={sqft} | walls={len(house_input.wall_segments)} | framing={house_input.framing_method} ═══")

    flooring_zones = house_input.flooring_zones
    if not flooring_zones:
        flooring_zones = [FlooringZone(material="vinyl_plank", sqft=sqft)]

    roof = house_input.roof
    if not roof:
        roof = RoofInput(type="gable", pitch=6, material="architectural_shingles")

    paint = house_input.paint
    if not paint:
        paint = PaintInput(material="standard_eggshell")

    if has_walls:
        base_costs = {
            "concrete": data.BASE_MATERIAL_COSTS["concrete"],
            "lumber":   data.FLOOR_FRAMING_COST_PER_SQFT,
        }
        log.info(f"Path: WALL MODEL active — lumber reduced to floor framing (${data.FLOOR_FRAMING_COST_PER_SQFT}/sqft)")
    else:
        base_costs = data.BASE_MATERIAL_COSTS
        log.info("Path: FALLBACK — using per-sqft estimates for all materials")

    material_total, material_breakdown = calculate_material_costs(sqft, flooring_zones, base_costs)
    log.debug(f"Base + flooring costs: { {k: f'${v:,.2f}' for k, v in material_breakdown.items()} }")

    wall_result = None
    if has_walls:
        wall_result = calculate_wall_costs(house_input.wall_segments, house_input.framing_method)
        material_breakdown.update(wall_result["breakdown"])
        material_total += wall_result["total_cost"]

        ceiling_drywall_cost = sqft * catalog.DRYWALL_PRICE_PER_SQFT
        material_breakdown["drywall"] += ceiling_drywall_cost
        material_total += ceiling_drywall_cost
        log.debug(f"Ceiling drywall: {sqft} sqft → ${ceiling_drywall_cost:,.2f}")

    roofing_cost, roof_area = calculate_roofing_cost(sqft, roof)
    material_breakdown["roofing"] = roofing_cost
    material_total += roofing_cost
    log.debug(f"Roofing: {roof_area} sqft → ${roofing_cost:,.2f}")

    geometry_sqft = wall_result["drywall_sqft"] if wall_result else None
    paint_cost, wall_area, paint_area_source = calculate_paint_cost(sqft, paint, geometry_sqft)
    material_breakdown["paint"] = paint_cost
    material_total += paint_cost
    log.debug(f"Paint: {wall_area} sqft ({paint_area_source}) → ${paint_cost:,.2f}")

    multiplier     = data.REGIONAL_ADJUSTMENTS["material_cost_multiplier"]
    pre_multiplier = material_total
    material_total *= multiplier
    log.info(f"Regional multiplier: {multiplier:.2f}x | ${pre_multiplier:,.2f} → ${material_total:,.2f}")

    appliance_total, appliance_breakdown = calculate_appliance_cost(house_input.appliances)
    material_breakdown["appliances"] = appliance_total
    material_total += appliance_total
    log.debug(f"Appliances: ${appliance_total:,.2f} ({len(appliance_breakdown)} item type(s))")

    permits_total = calculate_permit_costs(sqft)
    total_cost    = material_total + permits_total
    log.info(f"Permits: ${permits_total:,.2f}")
    log.info(f"─── TOTAL: ${total_cost:,.2f} (${total_cost / sqft:.2f}/sqft) ───")

    return {
        "materials":     dollars(material_total),
        "permits":       dollars(permits_total),
        "total_cost":    dollars(total_cost),
        "cost_per_sqft": dollars(total_cost / sqft),
        "selections": {
            "flooring":   format_flooring_selections(flooring_zones),
            "roofing":    [format_roofing_selection(roof, roof_area, roofing_cost)],
            "paint":      [format_paint_selection(paint, wall_area, paint_cost, paint_area_source)],
            "appliances": format_appliance_selections(house_input.appliances),
            "walls":      format_wall_selections(house_input, wall_result),
        },
        "cost_breakdown": {
            "materials": {k: dollars(v) for k, v in material_breakdown.items()}
        },
    }
