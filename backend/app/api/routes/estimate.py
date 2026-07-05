import logging

from fastapi import APIRouter, HTTPException
from app.models.estimate import HouseInput, HouseEstimate
from app.services.cost_engine import generate_estimate
from app.services.datasets import materials_catalog as catalog

router = APIRouter()
log = logging.getLogger(__name__)

VALID_ROOF_TYPES = list(catalog.ROOF_TYPE_MULTIPLIERS.keys())
FLAT_ONLY_MATERIALS = [key for key, opt in catalog.ROOFING.items() if opt.get("flat_only")]


def validate_house_input(house_input: HouseInput) -> list[str]:
    warnings = []

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

        if roof.pitch is not None and not 0 <= roof.pitch <= 12:
            raise HTTPException(
                status_code=422,
                detail=f"Roof pitch must be between 0 and 12. Got {roof.pitch}."
            )
        

        if roof.type == "flat" and roof.pitch is not None and roof.pitch > 0:
            raise HTTPException(
                status_code=422,
                detail=f"Roof type is 'flat' but pitch is {roof.pitch}. A flat roof must have a pitch of 0."
            )

    if house_input.paint:
        if house_input.paint.material not in catalog.PAINT:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid paint material '{house_input.paint.material}'. Valid options are: {list(catalog.PAINT.keys())}"
            )

        if not house_input.paint.wall_sqft and not house_input.wall_segments:
            warnings.append(
                "No wall_sqft provided for paint. Wall area was estimated at 2x floor sqft. "
                "For a more accurate number, provide wall_segments or exact wall_sqft."
            )

    for selection in house_input.appliances:
        if selection.appliance not in catalog.APPLIANCES:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid appliance '{selection.appliance}'. Valid options are: {list(catalog.APPLIANCES.keys())}"
            )

    if house_input.wall_segments:
        wall_ids = {wall.id for wall in house_input.wall_segments}

        for wall in house_input.wall_segments:

            if wall.id in wall.connected_wall_ids:
                raise HTTPException(
                    status_code=422,
                    detail=f"Wall '{wall.id}': a wall cannot list itself in connected_wall_ids."
                )

            if len(wall.connected_wall_ids) > 2:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Wall '{wall.id}': {len(wall.connected_wall_ids)} connected_wall_ids provided. "
                        f"A wall has 2 endpoints so the max is 2."
                    )
                )

            for connected_id in wall.connected_wall_ids:
                if connected_id not in wall_ids:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"Wall '{wall.id}': connected_wall_id '{connected_id}' "
                            f"does not match any wall in wall_segments."
                        )
                    )

            for opening in wall.openings:
                if opening.position + opening.width > wall.length:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"Wall '{wall.id}': opening at position {opening.position}ft "
                            f"with width {opening.width}ft extends past the wall end ({wall.length}ft)."
                        )
                    )

                if opening.height >= wall.height:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"Wall '{wall.id}': opening height {opening.height}ft must be "
                            f"less than wall height {wall.height}ft."
                        )
                    )

            sorted_openings = sorted(wall.openings, key=lambda o: o.position)
            for i in range(len(sorted_openings) - 1):
                a = sorted_openings[i]
                b = sorted_openings[i + 1]
                if a.position + a.width > b.position:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            f"Wall '{wall.id}': openings overlap. "
                            f"Opening at position {a.position}ft (width {a.width}ft) "
                            f"overlaps opening at position {b.position}ft."
                        )
                    )

    return warnings


@router.post("/estimate", response_model=HouseEstimate)
def create_estimate(house_input: HouseInput):
    log.info(f"POST /estimate — sqft={house_input.square_footage}, flooring_zones={len(house_input.flooring_zones)}, walls={len(house_input.wall_segments)}, appliances={len(house_input.appliances)}")

    warnings = validate_house_input(house_input)
    result = generate_estimate(house_input)
    result["warnings"] = warnings
    return result
