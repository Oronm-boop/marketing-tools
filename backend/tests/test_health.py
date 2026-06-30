from fastapi.testclient import TestClient

from app.main import create_app


def test_health_declares_backend_identity_and_browser_automation_feature():
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "mdt-ai-backend"
    assert payload["features"]["browser_automation_show_window"] is True
