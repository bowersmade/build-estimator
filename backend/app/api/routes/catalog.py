from fastapi import APIRouter
from app.services.datasets import materials_catalog as catalog

router = APIRouter()


@router.get("/catalog/flooring")
def get_flooring_options():
    return {
        "flooring": [
            {
                "key": key,
                "display_name": option["display_name"],
                "price_per_sqft": option["price_per_sqft"],
            }
            for key, option in catalog.FLOORING.items()
        ]
    }


@router.get("/catalog/roofing")
def get_roofing_options():
    return {
        "roofing": [
            {
                "key": key,
                "display_name": option["display_name"],
                "price_per_sqft": option["price_per_sqft"],
                "flat_only": option.get("flat_only", False),
            }
            for key, option in catalog.ROOFING.items()
        ],
        "roof_types": list(catalog.ROOF_TYPE_MULTIPLIERS.keys()),
        "pitch_range": {"min": 0, "max": 12},
    }


@router.get("/catalog/paint")
def get_paint_options():
    return {
        "paint": [
            {
                "key": key,
                "display_name": option["display_name"],
                "price_per_sqft": option["price_per_sqft"],
            }
            for key, option in catalog.PAINT.items()
        ]
    }


@router.get("/catalog/appliances")
def get_appliance_options():
    return {
        "appliances": [
            {
                "key": key,
                "display_name": option["display_name"],
                "unit_price": option["unit_price"],
            }
            for key, option in catalog.APPLIANCES.items()
        ]
    }
