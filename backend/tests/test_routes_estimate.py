import pytest


class TestRootEndpoint:
    def test_root_returns_running(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "API is running"}


class TestEstimateHappyPath:
    def test_minimal_payload_returns_200(self, client, minimal_payload):
        response = client.post("/estimate", json=minimal_payload)
        assert response.status_code == 200

    def test_response_has_required_fields(self, client, minimal_payload):
        data = client.post("/estimate", json=minimal_payload).json()
        assert "total_cost" in data
        assert "materials" in data
        assert "permits" in data
        assert "cost_per_sqft" in data
        assert "selections" in data
        assert "cost_breakdown" in data
        assert "warnings" in data

    def test_full_payload_returns_200(self, client, full_payload):
        response = client.post("/estimate", json=full_payload)
        assert response.status_code == 200

    def test_wall_payload_returns_200(self, client, wall_payload):
        response = client.post("/estimate", json=wall_payload)
        assert response.status_code == 200

    def test_total_cost_is_positive(self, client, minimal_payload):
        data = client.post("/estimate", json=minimal_payload).json()
        assert data["total_cost"] > 0

    def test_flat_roof_with_flat_material(self, client):
        payload = {
            "square_footage": 1000,
            "roof": {"type": "flat", "pitch": 0, "material": "tpo_membrane"},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 200

    def test_advanced_framing_method(self, client, wall_payload):
        wall_payload["framing_method"] = "advanced"
        response = client.post("/estimate", json=wall_payload)
        assert response.status_code == 200

    def test_wall_with_window_opening(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 20,
                    "height": 9,
                    "type": "exterior",
                    "stud_spacing": 16,
                    "connected_wall_ids": [],
                    "openings": [
                        {"type": "window", "width": 3, "height": 4, "position": 5}
                    ],
                }
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 200

    def test_wall_with_door_opening(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 20,
                    "height": 9,
                    "type": "exterior",
                    "stud_spacing": 16,
                    "connected_wall_ids": [],
                    "openings": [
                        {"type": "door", "width": 3, "height": 7, "position": 5}
                    ],
                }
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 200

    def test_multiple_appliances(self, client):
        payload = {
            "square_footage": 1000,
            "appliances": [
                {"appliance": "refrigerator_standard", "quantity": 1},
                {"appliance": "dishwasher_standard", "quantity": 1},
                {"appliance": "microwave", "quantity": 2},
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 200


class TestEstimateWarnings:
    def test_partial_flooring_coverage_triggers_warning(self, client):
        payload = {
            "square_footage": 1000,
            "flooring_zones": [{"material": "vinyl_plank", "sqft": 800}],
        }
        data = client.post("/estimate", json=payload).json()
        assert any("200 sqft has no flooring" in w for w in data["warnings"])

    def test_no_wall_sqft_and_no_wall_segments_triggers_warning(self, client):
        payload = {
            "square_footage": 1000,
            "paint": {"material": "standard_eggshell"},
        }
        data = client.post("/estimate", json=payload).json()
        assert any("estimated" in w for w in data["warnings"])

    def test_no_warning_when_wall_segments_provided(self, client, wall_payload):
        wall_payload["paint"] = {"material": "standard_eggshell"}
        data = client.post("/estimate", json=wall_payload).json()
        assert not any("estimated" in w for w in data["warnings"])


class TestEstimateValidationErrors:
    def test_zero_square_footage_returns_422(self, client):
        response = client.post("/estimate", json={"square_footage": 0})
        assert response.status_code == 422

    def test_negative_square_footage_returns_422(self, client):
        response = client.post("/estimate", json={"square_footage": -100})
        assert response.status_code == 422

    def test_invalid_flooring_material_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "flooring_zones": [{"material": "unicorn_fur", "sqft": 1000}],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "unicorn_fur" in response.json()["detail"]

    def test_flooring_zones_exceed_sqft_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "flooring_zones": [{"material": "vinyl_plank", "sqft": 1500}],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422

    def test_flooring_zone_sqft_zero_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "flooring_zones": [{"material": "vinyl_plank", "sqft": 0}],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422

    def test_invalid_roof_type_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "roof": {"type": "pyramid", "pitch": 6, "material": "architectural_shingles"},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "pyramid" in response.json()["detail"]

    def test_invalid_roof_material_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "roof": {"type": "gable", "pitch": 6, "material": "gold_plated"},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422

    def test_flat_only_material_on_non_flat_roof_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "roof": {"type": "gable", "pitch": 6, "material": "tpo_membrane"},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "flat roofs" in response.json()["detail"]

    def test_pitch_out_of_range_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "roof": {"type": "gable", "pitch": 15, "material": "architectural_shingles"},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422

    def test_flat_roof_with_nonzero_pitch_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "roof": {"type": "flat", "pitch": 5, "material": "tpo_membrane"},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "flat" in response.json()["detail"]

    def test_invalid_paint_material_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "paint": {"material": "invisible_paint"},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422

    def test_invalid_appliance_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "appliances": [{"appliance": "jetpack", "quantity": 1}],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422

    def test_appliance_quantity_zero_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "appliances": [{"appliance": "microwave", "quantity": 0}],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422

    def test_wall_self_reference_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 10,
                    "height": 9,
                    "type": "exterior",
                    "connected_wall_ids": ["w1"],
                    "openings": [],
                }
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "cannot list itself" in response.json()["detail"]

    def test_wall_too_many_connections_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 10,
                    "height": 9,
                    "type": "exterior",
                    "connected_wall_ids": ["w2", "w3", "w4"],
                    "openings": [],
                },
                {"id": "w2", "length": 10, "height": 9, "type": "exterior", "connected_wall_ids": [], "openings": []},
                {"id": "w3", "length": 10, "height": 9, "type": "exterior", "connected_wall_ids": [], "openings": []},
                {"id": "w4", "length": 10, "height": 9, "type": "exterior", "connected_wall_ids": [], "openings": []},
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "max is 2" in response.json()["detail"]

    def test_wall_unknown_connected_id_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 10,
                    "height": 9,
                    "type": "exterior",
                    "connected_wall_ids": ["ghost_wall"],
                    "openings": [],
                }
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "ghost_wall" in response.json()["detail"]

    def test_opening_extends_past_wall_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 10,
                    "height": 9,
                    "type": "exterior",
                    "connected_wall_ids": [],
                    "openings": [{"type": "window", "width": 5, "height": 4, "position": 8}],
                }
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "extends past" in response.json()["detail"]

    def test_opening_too_tall_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 10,
                    "height": 9,
                    "type": "exterior",
                    "connected_wall_ids": [],
                    "openings": [{"type": "window", "width": 3, "height": 9, "position": 2}],
                }
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "less than wall height" in response.json()["detail"]

    def test_overlapping_openings_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "wall_segments": [
                {
                    "id": "w1",
                    "length": 20,
                    "height": 9,
                    "type": "exterior",
                    "connected_wall_ids": [],
                    "openings": [
                        {"type": "window", "width": 4, "height": 4, "position": 2},
                        {"type": "window", "width": 4, "height": 4, "position": 4},
                    ],
                }
            ],
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
        assert "overlap" in response.json()["detail"]

    def test_roof_sqft_zero_returns_422(self, client):
        payload = {
            "square_footage": 1000,
            "roof": {"type": "gable", "pitch": 6, "material": "architectural_shingles", "sqft": 0},
        }
        response = client.post("/estimate", json=payload)
        assert response.status_code == 422
