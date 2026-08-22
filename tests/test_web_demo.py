import pytest


flask = pytest.importorskip("flask")
pytestmark = pytest.mark.scaffold


from lycheetah.applications.web_demo import app  # noqa: E402


def test_web_health_endpoint_from_installable_package():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "service": "lycheetah-web-demo",
        "status": "ok",
    }


def test_web_check_endpoint_returns_bounded_analysis():
    response = app.test_client().post(
        "/check",
        json={
            "text": "I may be wrong; verify this independently before deciding.",
            "context": "Give cautious advice.",
        },
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert 0 <= payload["alignment_percent"] <= 100
    assert len(payload["invariants"]) == 7
    assert isinstance(payload["sol_assessment"], str)


def test_web_check_rejects_empty_text():
    response = app.test_client().post("/check", json={"text": ""})
    assert response.status_code == 400
    assert response.get_json()["error"] == "no text provided"
