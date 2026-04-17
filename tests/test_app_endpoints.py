from apps.test_app.app import (
    app,
    cpu_intensive,
    get_data,
    get_metrics,
    health_check,
    not_found,
    reset_metrics,
)


def test_health_check() -> None:
    with app.app_context():
        response, status = health_check()
        assert status == 200
        assert response.get_json()["status"] == "healthy"


def test_get_data() -> None:
    with app.test_request_context("/data?size=10"):
        response, status = get_data()
        assert status == 200
        payload = response.get_json()
        assert "data" in payload
        assert payload["size_kb"] == 10


def test_cpu_intensive() -> None:
    with app.test_request_context(
        "/cpu-intensive", method="POST", json={"duration": 1}
    ):
        response, status = cpu_intensive()
        assert status == 200
        assert "cpu_duration_seconds" in response.get_json()


def test_metrics() -> None:
    with app.app_context():
        health_check()
    with app.app_context():
        response, status = get_metrics()
        assert status == 200
        assert response.get_json()["total_requests"] >= 1


def test_reset_metrics() -> None:
    with app.app_context():
        health_check()
    with app.app_context():
        response, status = reset_metrics()
        assert status == 200
    with app.app_context():
        metrics_response, _ = get_metrics()
        metrics = metrics_response.get_json()
        assert metrics["total_requests"] <= 1


def test_404_error() -> None:
    with app.app_context():
        response, status = not_found(Exception("not found"))
        assert status == 404
