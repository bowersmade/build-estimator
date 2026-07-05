import logging
import math
from collections import defaultdict

from app.services.datasets import st_george as data
from app.services.datasets import materials_catalog as catalog

log = logging.getLogger(__name__)


def calculate_material_costs(sqft: int, flooring_zones: list, base_costs: dict = None):
    if base_costs is None:
        base_costs = data.BASE_MATERIAL_COSTS

    material_costs = {}
    total = 0

    for material, cost_per_sqft in base_costs.items():
        cost = sqft * cost_per_sqft
        material_costs[material] = cost
        total += cost

    flooring_total = 0
    for zone in flooring_zones:
        option = catalog.FLOORING[zone.material]
        flooring_total += zone.sqft * option["price_per_sqft"]

    material_costs["flooring"] = flooring_total
    total += flooring_total

    return total, material_costs


def calculate_roof_area(floor_sqft: int, roof_input) -> float:
    if roof_input.sqft:
        return float(roof_input.sqft)

    slope_factor = math.sqrt(1 + (roof_input.pitch / 12) ** 2)
    type_multiplier = catalog.ROOF_TYPE_MULTIPLIERS.get(roof_input.type, 1.0)

    return floor_sqft * slope_factor * type_multiplier


def calculate_roofing_cost(floor_sqft: int, roof_input):
    option = catalog.ROOFING[roof_input.material]
    roof_area = calculate_roof_area(floor_sqft, roof_input)
    total = roof_area * option["price_per_sqft"]

    return total, round(roof_area)


def calculate_paint_cost(floor_sqft: int, paint_input, geometry_sqft: float = None):
    if paint_input.wall_sqft:
        wall_area = float(paint_input.wall_sqft)
        area_source = "provided walls + ceiling"
    elif geometry_sqft is not None:
        wall_area = geometry_sqft
        area_source = "wall geometry + ceiling"
    else:
        wall_area = floor_sqft * catalog.WALL_AREA_ESTIMATE_MULTIPLIER
        area_source = "estimated walls + ceiling"

    total_area = wall_area + floor_sqft

    option = catalog.PAINT[paint_input.material]
    total = total_area * option["price_per_sqft"]

    return total, round(total_area), area_source


def calculate_appliance_cost(appliance_selections: list):
    appliance_costs = {}
    total = 0

    for selection in appliance_selections:
        option = catalog.APPLIANCES[selection.appliance]
        line_total = option["unit_price"] * selection.quantity
        appliance_costs[selection.appliance] = appliance_costs.get(selection.appliance, 0) + line_total
        total += line_total

    return total, appliance_costs


def calculate_permit_costs(sqft: int):
    base = data.PERMIT_FEES["base"]
    per_square_foot = data.PERMIT_FEES["per_square_foot"]

    return base + (sqft * per_square_foot)


def _get_header_spec(opening_width_ft: float) -> tuple[str, float]:
    for max_width, lumber_type, depth_inches in catalog.HEADER_SPECS:
        if max_width is None or opening_width_ft <= max_width:
            return lumber_type, depth_inches
    return "lvl", 9.5  # pragma: no cover


def calculate_wall_costs(wall_segments: list, framing_method: str = "traditional") -> dict:
    total_lumber_cost     = 0.0
    total_lumber_lf       = 0.0
    total_drywall_sqft    = 0.0
    total_sheathing_sqft  = 0.0
    total_insulation_sqft = 0.0
    total_window_cost     = 0.0
    total_door_cost       = 0.0

    log.info(f"─── Wall model: {len(wall_segments)} wall(s), framing={framing_method} ───")

    for wall in wall_segments:
        length_ft     = wall.length
        height_ft     = wall.height
        length_inches = length_ft * 12
        spacing_in    = wall.stud_spacing
        stud_type     = "2x6" if wall.type == "exterior" else "2x4"

        log.debug(f"Wall '{wall.id}' | {wall.type} | {wall.length:.1f}ft × {wall.height:.1f}ft | {wall.stud_spacing}\" OC | studs={stud_type}")

        lumber_lf: dict = defaultdict(float)

        lumber_lf[stud_type] += 3 * length_ft
        log.debug(f"  Plates: {3 * length_ft:.1f} LF of {stud_type} (3 × {length_ft:.1f}ft)")

        base_studs      = math.floor(length_inches / spacing_in) + 1
        num_connections = len(wall.connected_wall_ids)
        corner_adjustment = num_connections * 1 if framing_method == "traditional" else 0

        log.debug(f"  Studs: base={base_studs} | connections={num_connections} | corner_adj={corner_adjustment:+d}")

        opening_stud_delta = 0
        total_jack_lf      = 0.0

        for opening in wall.openings:
            width_ft     = opening.width
            width_inches = width_ft * 12

            studs_removed  = max(0, math.floor(width_inches / spacing_in) - 1)
            cripples_above = max(0, math.floor(width_inches / spacing_in) - 1)
            cripples_below = (
                max(0, math.floor(width_inches / spacing_in) - 1)
                if opening.type == "window"
                else 0
            )

            opening_stud_delta += -studs_removed + cripples_above + cripples_below

            log.debug(f"  Opening: {opening.type} {opening.width:.1f}ft × {opening.height:.1f}ft @ {opening.position:.1f}ft | "
                      f"removed={studs_removed}, cripples_above={cripples_above}, cripples_below={cripples_below}")

            header_type, header_depth_in = _get_header_spec(width_ft)
            bearing_allowance_ft = (2 * 3.5) / 12
            header_board_lf      = width_ft + bearing_allowance_ft
            lumber_lf[header_type] += 2 * header_board_lf

            if opening.type == "window":
                lumber_lf[stud_type] += width_ft + bearing_allowance_ft

            jack_height_ft = height_ft - (header_depth_in / 12)
            total_jack_lf += 2 * jack_height_ft

            log.debug(f"    header={header_type} (depth={header_depth_in:.2f}\"), jack_height={jack_height_ft:.2f}ft, "
                      f"header_lf={2 * header_board_lf:.2f}, jack_lf={2 * jack_height_ft:.2f}")

            opening_area_sqft = opening.width * opening.height
            if opening.type == "window":
                total_window_cost += opening_area_sqft * catalog.WINDOW_PRICE_PER_SQFT
            else:
                total_door_cost += opening_area_sqft * catalog.DOOR_PRICE_PER_SQFT

        regular_studs = base_studs + corner_adjustment + opening_stud_delta
        lumber_lf[stud_type] += regular_studs * height_ft
        lumber_lf[stud_type] += total_jack_lf

        log.debug(f"  Adjusted studs: {regular_studs} (base={base_studs}, corner_adj={corner_adjustment:+d}, opening_delta={opening_stud_delta:+d})")
        log.debug(f"  Jack stud LF: {total_jack_lf:.2f} | Stud LF: {regular_studs * height_ft:.2f}")

        wall_lumber_lf   = sum(lumber_lf.values())
        wall_lumber_cost = sum(lf * catalog.LUMBER_PRICES[bt] for bt, lf in lumber_lf.items())

        log.debug(f"  Lumber by type: { {bt: f'{lf:.1f}LF' for bt, lf in lumber_lf.items()} }")
        log.debug(f"  Lumber total: {wall_lumber_lf:.1f} LF → ${wall_lumber_cost:.2f}")

        for board_type, lf in lumber_lf.items():
            total_lumber_lf   += lf
            total_lumber_cost += lf * catalog.LUMBER_PRICES[board_type]

        gross_area   = length_ft * height_ft
        opening_area = sum(o.width * o.height for o in wall.openings)
        net_area     = gross_area - opening_area

        if wall.type == "exterior":
            total_drywall_sqft    += net_area
            total_sheathing_sqft  += net_area
            total_insulation_sqft += net_area
        elif wall.type == "interior_finished":
            total_drywall_sqft += net_area * 2

        log.debug(f"  Surface: gross={gross_area:.1f}, openings={opening_area:.1f}, net={net_area:.1f} sqft | type={wall.type}")

    drywall_cost    = total_drywall_sqft    * catalog.DRYWALL_PRICE_PER_SQFT
    sheathing_cost  = total_sheathing_sqft  * catalog.SHEATHING_PRICE_PER_SQFT
    insulation_cost = total_insulation_sqft * catalog.INSULATION_PRICE_PER_SQFT

    total_cost = (
        total_lumber_cost
        + drywall_cost
        + sheathing_cost
        + insulation_cost
        + total_window_cost
        + total_door_cost
    )

    log.info("Wall model totals:")
    log.info(f"  Lumber:     {total_lumber_lf:7.1f} LF  → ${total_lumber_cost:,.2f}")
    log.info(f"  Drywall:    {total_drywall_sqft:7.1f} sqft → ${drywall_cost:,.2f}")
    log.info(f"  Sheathing:  {total_sheathing_sqft:7.1f} sqft → ${sheathing_cost:,.2f}")
    log.info(f"  Insulation: {total_insulation_sqft:7.1f} sqft → ${insulation_cost:,.2f}")
    log.info(f"  Windows:                  ${total_window_cost:,.2f}")
    log.info(f"  Doors:                    ${total_door_cost:,.2f}")
    log.info(f"  Wall subtotal:            ${total_cost:,.2f}")

    return {
        "total_cost":       total_cost,
        "lumber_lf":        round(total_lumber_lf,      2),
        "drywall_sqft":     round(total_drywall_sqft,   2),
        "sheathing_sqft":   round(total_sheathing_sqft, 2),
        "insulation_sqft":  round(total_insulation_sqft, 2),
        "breakdown": {
            "lumber":      total_lumber_cost,
            "drywall":     drywall_cost,
            "sheathing":   sheathing_cost,
            "insulation":  insulation_cost,
            "windows":     total_window_cost,
            "doors":       total_door_cost,
        },
    }
