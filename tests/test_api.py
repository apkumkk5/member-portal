"""Tests for the member portal.

Phase 3 of the lifecycle expands these. For now they cover the paths that
would break a deploy: health, listing, retrieval, update, and download.
"""

import pytest
from fastapi.testclient import TestClient

from app.db import get_all_members, get_member, update_member
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


def test_seed_resets_ids_from_one():
    """A reset must clear the AUTOINCREMENT counter, not just the rows.

    Without clearing sqlite_sequence, re-seeding produces IDs 26-30 instead
    of 1-5, and every test referencing member 1 breaks. This guards the fix.
    """
    seed(count=5)

    ids = [m["id"] for m in get_all_members()]
    assert sorted(ids) == [1, 2, 3, 4, 5]


def test_language_preference_persists_across_reads():
    """An update must be durable, not just reflected in the redirect."""
    client = TestClient(app)
    client.post(
        "/members/2/edit",
        data={
            "email": "persist@example.com",
            "phone": "555-0199",
            "address_line1": "9 Persist Ave",
            "city": "Trenton",
            "state": "NJ",
            "postal_code": "08608",
            "language_preference": "vi",
        },
        follow_redirects=False,
    )

    member = get_member(2)
    assert member["language_preference"] == "vi"
    assert member["email"] == "persist@example.com"


def test_member_number_cannot_be_changed():
    """The update allowlist must reject fields members shouldn't control."""
    before = get_member(3)["member_number"]
    update_member(3, {"member_number": "M999999", "city": "Edison"})
    after = get_member(3)

    assert after["member_number"] == before
    assert after["city"] == "Edison"
