from crosswalk_api import create_app
from crosswalk_api.errors import ApiInputError
from fastapi.testclient import TestClient


def test_error_envelope_has_stable_shape() -> None:
    app = create_app()

    @app.get("/bad")
    def bad() -> None:
        raise ApiInputError("bad field")

    response = TestClient(app).get("/bad")
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_input"
