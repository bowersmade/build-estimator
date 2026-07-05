from app.services.datasets import materials_catalog as catalog


def dollars(value: float) -> float:
    return round(value, 2)


def format_flooring_selections(flooring_zones: list) -> list[str]:
    selections = []
    for zone in flooring_zones:
        option    = catalog.FLOORING[zone.material]
        zone_cost = zone.sqft * option["price_per_sqft"]
        label     = zone.room if zone.room else "Unassigned"
        selections.append(
            f"{label}: {option['display_name']} "
            f"(${option['price_per_sqft']}/sqft x {zone.sqft} sqft = ${dollars(zone_cost):,.2f})"
        )
    return selections


def format_roofing_selection(roof, roof_area: int, roofing_cost: float) -> str:
    option      = catalog.ROOFING[roof.material]
    area_source = "provided" if roof.sqft else f"calculated from {roof.pitch}/12 pitch"
    return (
        f"{roof.type.capitalize()} roof, {roof.pitch}/12 pitch — "
        f"{option['display_name']} "
        f"(${option['price_per_sqft']}/sqft x {roof_area} sqft [{area_source}] "
        f"= ${dollars(roofing_cost):,.2f})"
    )


def format_paint_selection(paint, wall_area: int, paint_cost: float, area_source: str) -> str:
    option = catalog.PAINT[paint.material]
    return (
        f"{option['display_name']} "
        f"(${option['price_per_sqft']}/sqft x {wall_area} sqft [{area_source}] "
        f"= ${dollars(paint_cost):,.2f})"
    )


def format_appliance_selections(appliances: list) -> list[str]:
    selections = []
    for selection in appliances:
        option     = catalog.APPLIANCES[selection.appliance]
        line_total = option["unit_price"] * selection.quantity
        selections.append(
            f"{option['display_name']} x{selection.quantity} "
            f"@ ${option['unit_price']:,} each = ${dollars(line_total):,.2f}"
        )
    return selections


def format_wall_selections(house_input, wall_result) -> list[str]:
    if wall_result:
        return [
            f"{len(house_input.wall_segments)} wall segment(s) — "
            f"lumber: {wall_result['lumber_lf']} LF, "
            f"drywall: {wall_result['drywall_sqft']} sqft, "
            f"sheathing: {wall_result['sheathing_sqft']} sqft, "
            f"insulation: {wall_result['insulation_sqft']} sqft"
        ]
    return [
        "No wall segments provided — using per-sqft estimates for "
        "lumber, drywall, insulation, windows, and doors."
    ]
