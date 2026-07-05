class TestCatalogFlooring:
    def test_returns_200(self, client):
        response = client.get("/catalog/flooring")
        assert response.status_code == 200

    def test_contains_flooring_key(self, client):
        data = client.get("/catalog/flooring").json()
        assert "flooring" in data

    def test_each_item_has_required_fields(self, client):
        data = client.get("/catalog/flooring").json()
        for item in data["flooring"]:
            assert "key" in item
            assert "display_name" in item
            assert "price_per_sqft" in item

    def test_vinyl_plank_is_present(self, client):
        data = client.get("/catalog/flooring").json()
        keys = [item["key"] for item in data["flooring"]]
        assert "vinyl_plank" in keys


class TestCatalogRoofing:
    def test_returns_200(self, client):
        response = client.get("/catalog/roofing")
        assert response.status_code == 200

    def test_contains_roofing_and_roof_types(self, client):
        data = client.get("/catalog/roofing").json()
        assert "roofing" in data
        assert "roof_types" in data
        assert "pitch_range" in data

    def test_each_item_has_required_fields(self, client):
        data = client.get("/catalog/roofing").json()
        for item in data["roofing"]:
            assert "key" in item
            assert "display_name" in item
            assert "price_per_sqft" in item
            assert "flat_only" in item

    def test_pitch_range_correct(self, client):
        data = client.get("/catalog/roofing").json()
        assert data["pitch_range"]["min"] == 0
        assert data["pitch_range"]["max"] == 12

    def test_flat_only_materials_flagged(self, client):
        data = client.get("/catalog/roofing").json()
        tpo = next(i for i in data["roofing"] if i["key"] == "tpo_membrane")
        assert tpo["flat_only"] is True

    def test_non_flat_materials_not_flagged(self, client):
        data = client.get("/catalog/roofing").json()
        shingles = next(i for i in data["roofing"] if i["key"] == "architectural_shingles")
        assert shingles["flat_only"] is False


class TestCatalogPaint:
    def test_returns_200(self, client):
        response = client.get("/catalog/paint")
        assert response.status_code == 200

    def test_contains_paint_key(self, client):
        data = client.get("/catalog/paint").json()
        assert "paint" in data

    def test_each_item_has_required_fields(self, client):
        data = client.get("/catalog/paint").json()
        for item in data["paint"]:
            assert "key" in item
            assert "display_name" in item
            assert "price_per_sqft" in item

    def test_standard_eggshell_present(self, client):
        data = client.get("/catalog/paint").json()
        keys = [item["key"] for item in data["paint"]]
        assert "standard_eggshell" in keys


class TestCatalogAppliances:
    def test_returns_200(self, client):
        response = client.get("/catalog/appliances")
        assert response.status_code == 200

    def test_contains_appliances_key(self, client):
        data = client.get("/catalog/appliances").json()
        assert "appliances" in data

    def test_each_item_has_required_fields(self, client):
        data = client.get("/catalog/appliances").json()
        for item in data["appliances"]:
            assert "key" in item
            assert "display_name" in item
            assert "unit_price" in item

    def test_refrigerator_present(self, client):
        data = client.get("/catalog/appliances").json()
        keys = [item["key"] for item in data["appliances"]]
        assert "refrigerator_standard" in keys
