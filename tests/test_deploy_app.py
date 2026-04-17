from __future__ import annotations

from deployment.deploy_app import (
    build_asg_subnet_identifier,
    build_user_data,
    extract_alb_dns,
)


def test_extract_alb_dns_supports_existing_key() -> None:
    config = {"alb_dns": "example-alb.us-east-1.elb.amazonaws.com"}
    assert extract_alb_dns(config) == "example-alb.us-east-1.elb.amazonaws.com"


def test_extract_alb_dns_supports_alternative_key() -> None:
    config = {"alb_dns_name": "other-alb.us-east-1.elb.amazonaws.com"}
    assert extract_alb_dns(config) == "other-alb.us-east-1.elb.amazonaws.com"


def test_build_user_data_embeds_flask_app() -> None:
    app_source = "print('hello')\n"
    rendered = build_user_data(app_source=app_source)

    assert "cat > /opt/test_app/app.py <<'PYAPP'" in rendered
    assert "print('hello')" in rendered
    assert "ExecStart=/usr/bin/python3 /opt/test_app/app.py" in rendered
    assert "systemctl enable test-app.service" in rendered


def test_build_asg_subnet_identifier_joins_values() -> None:
    result = build_asg_subnet_identifier(
        ["subnet-aaa111", "subnet-bbb222", "subnet-ccc333"]
    )
    assert result == "subnet-aaa111,subnet-bbb222,subnet-ccc333"
