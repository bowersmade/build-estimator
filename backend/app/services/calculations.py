import math

from app.services.datasets import st_george as data
from app.services.datasets import materials_catalog as catalog


def calculate_material_costs(sqft: int, flooring_zones: list):
    material_costs = {}
    total = 0

    for material, cost_per_sqft in data.BASE_MATERIAL_COSTS.items():
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
    # If the Sims engine sent exact sqft, use it — no estimation needed.
    if roof_input.sqft:
        return float(roof_input.sqft)

    # Fallback: estimate from pitch and type. Used when sqft is not provided
    # (e.g., bare API calls without a game engine).
    # If pitch is also None, default to 6/12 — a common residential slope that
    # gives a reasonable area estimate without any user input.
    pitch = roof_input.pitch if roof_input.pitch is not None else 6
    slope_factor = math.sqrt(1 + (pitch / 12) ** 2)
    type_multiplier = catalog.ROOF_TYPE_MULTIPLIERS.get(roof_input.type, 1.0)

    return floor_sqft * slope_factor * type_multiplier


def calculate_roofing_cost(floor_sqft: int, roof_input):
    option = catalog.ROOFING[roof_input.material]
    roof_area = calculate_roof_area(floor_sqft, roof_input)
    total = roof_area * option["price_per_sqft"]

    return total, round(roof_area)


def calculate_paint_cost(floor_sqft: int, paint_input):
    if paint_input.wall_sqft:
        wall_area = float(paint_input.wall_sqft)
        area_source = "provided"
    else:
        wall_area = floor_sqft * catalog.WALL_AREA_ESTIMATE_MULTIPLIER
        area_source = "estimated"

    option = catalog.PAINT[paint_input.material]
    total = wall_area * option["price_per_sqft"]

    return total, round(wall_area), area_source


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
