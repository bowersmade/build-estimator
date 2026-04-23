from fastapi import APIRouter, HTTPException
from app.models.estimate import HouseInput, HouseEstimate
from app.services.cost_engine import generate_estimate
from app.services.datasets import materials_catalog as catalog

router = APIRouter()

VALID_ROOF_TYPES = list(catalog.ROOF_TYPE_MULTIPLIERS.keys())
FLAT_ONLY_MATERIALS = [key for key, opt in catalog.ROOFING.items() if opt.get("flat_only")]


def validate_house_input(house_input: HouseInput) -> list[str]:
    warnings = []

    # ---- Flooring ----
    valid_flooring_keys = list(catalog.FLOORING.keys())

    for zone in house_input.flooring_zones:
        if zone.material not in catalog.FLOORING:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid flooring material '{zone.material}'. Valid options are: {valid_flooring_keys}"
            )

    if house_input.flooring_zones:
        total_zone_sqft = sum(zone.sqft for zone in house_input.flooring_zones)

        if total_zone_sqft > house_input.square_footage:
            raise HTTPException(
                status_code=422,
                detail=f"Flooring zones total {total_zone_sqft} sqft but the house is only {house_input.square_footage} sqft. Zones cannot exceed total square footage."
            )

        if total_zone_sqft < house_input.square_footage:
            uncovered = house_input.square_footage - total_zone_sqft
            warnings.append(
                f"Flooring zones only cover {total_zone_sqft} sqft of {house_input.square_footage} sqft. {uncovered} sqft has no flooring selected."
            )

    # ---- Roofing ----
    if house_input.roof:
        roof = house_input.roof

        if roof.type not in VALID_ROOF_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid roof type '{roof.type}'. Valid options are: {VALID_ROOF_TYPES}"
            )

        if roof.material not in catalog.ROOFING:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid roofing material '{roof.material}'. Valid options are: {list(catalog.ROOFING.keys())}"
            )

        if roof.material in FLAT_ONLY_MATERIALS and roof.type != "flat":
            raise HTTPException(
                status_code=422,
                detail=f"'{roof.material}' can only be used on flat roofs. Choose a different material or set roof type to 'flat'."
            )

        # Pitch is optional. When provided, still validate the range so bad data
        # doesn't silently produce garbage slope factors in the fallback calculation.
        if roof.pitch is not None and not 0 <= roof.pitch <= 12:
            raise HTTPException(
                status_code=422,
                detail=f"Roof pitch must be between 0 and 12. Got {roof.pitch}."
            )

    # ---- Paint ----
    if house_input.paint:
        if house_input.paint.material not in catalog.PAINT:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid paint material '{house_input.paint.material}'. Valid options are: {list(catalog.PAINT.keys())}"
            )

        if not house_input.paint.wall_sqft:
            warnings.append(
                "No wall_sqft provided for paint. Wall area was estimated at 2x floor sqft. "
                "For a more accurate number, provide the exact wall_sqft."
            )

    # ---- Appliances ----
    # Note: quantity >= 1 is enforced by the ApplianceSelection model (Field ge=1).
    # Pydantic returns a 422 before this function is called if quantity is invalid.
    # We only need to check that the appliance key exists in the catalog.
    for selection in house_input.appliances:
        if selection.appliance not in catalog.APPLIANCES:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid appliance '{selection.appliance}'. Valid options are: {list(catalog.APPLIANCES.keys())}"
            )

    return warnings


@router.post("/estimate", response_model=HouseEstimate)
def create_estimate(house_input: HouseInput):
    warnings = validate_house_input(house_input)
    result = generate_estimate(house_input)
    result["warnings"] = warnings
    return result
