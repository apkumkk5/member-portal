"""Tests for the member portal.

Phase 3 of the lifecycle expands these. For now they cover the paths that
would break a deploy: health, listing, retrieval, update, and download.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


@pytest.fixture(scope="module", autouse=True)
def seeded_db():
    seed(count=5)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Member" in response.text


def test_detail_page_renders(client):
    response = client.get("/members/1")
    assert response.status_code == 200


def test_unknown_member_returns_404(client):
    response = client.get("/members/9999")
    assert response.status_code == 404


def test_update_changes_language_preference(client):
    response = client.post(
        "/members/1/edit",
        data={
            "email": "updated@example.com",
            "phone": "555-0100",
            "address_line1": "1 Test St",
            "city": "Newark",
            "state": "NJ",
            "postal_code": "07102",
            "language_preference": "es",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    detail = client.get("/members/1")
    assert "updated@example.com" in detail.text
    assert "Spanish" in detail.text


def test_download_json(client):
    response = client.get("/members/1/download?format=json")
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    assert response.json()["member_number"].startswith("M")


def test_download_csv(client):
    response = client.get("/members/1/download?format=csv")
    assert response.status_code == 200
    assert "member_number" in response.text
