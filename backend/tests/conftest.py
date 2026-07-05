import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def minimal_payload():
    return {"square_footage": 1000}


@pytest.fixture
def full_payload():
    return {
        "square_footage": 1000,
        "flooring_zones": [{"material": "vinyl_plank", "sqft": 1000}],
        "roof": {"type": "gable", "pitch": 6, "material": "architectural_shingles"},
        "paint": {"material": "standard_eggshell"},
        "appliances": [{"appliance": "refrigerator_standard", "quantity": 1}],
    }


@pytest.fixture
def wall_payload():
    return {
        "square_footage": 1000,
        "wall_segments": [
            {
                "id": "w1",
                "length": 20,
                "height": 9,
                "type": "exterior",
                "stud_spacing": 16,
                "connected_wall_ids": ["w2"],
                "openings": [],
            },
            {
                "id": "w2",
                "length": 10,
                "height": 9,
                "type": "exterior",
                "stud_spacing": 16,
                "connected_wall_ids": ["w1"],
                "openings": [],
            },
        ],
    }
