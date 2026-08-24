import pytest

from app import create_app
from services.ticket_service import InMemoryTicketRepository


@pytest.fixture()
def client():
    app = create_app(testing=True, repository=InMemoryTicketRepository())
    return app.test_client()


@pytest.fixture()
def valid_ticket():
    return {
        "name": "Rishabh Shukla",
        "email": "rishabh@gmail.com",
        "category": "Network",
        "priority": "High",
        "description": "Unable to connect to campus Wi-Fi",
    }


def create_ticket(client, payload):
    return client.post("/api/tickets", json=payload)


def test_create_ticket_success(client, valid_ticket):
    response = create_ticket(client, valid_ticket)

    assert response.status_code == 201
    body = response.get_json()
    assert body["ticket"]["_id"].startswith("IT-")
    assert body["ticket"]["status"] == "Open"
    assert body["ticket"]["priority"] == "High"


def test_create_ticket_missing_email(client, valid_ticket):
    valid_ticket.pop("email")

    response = create_ticket(client, valid_ticket)

    assert response.status_code == 400
    assert "email" in response.get_json()["details"]


def test_create_ticket_invalid_email(client, valid_ticket):
    valid_ticket["email"] = "bad-email"

    response = create_ticket(client, valid_ticket)

    assert response.status_code == 400
    assert "email" in response.get_json()["details"]


def test_create_ticket_invalid_priority(client, valid_ticket):
    valid_ticket["priority"] = "Urgent"

    response = create_ticket(client, valid_ticket)

    assert response.status_code == 400
    assert "priority" in response.get_json()["details"]


def test_create_ticket_invalid_category(client, valid_ticket):
    valid_ticket["category"] = "Facilities"

    response = create_ticket(client, valid_ticket)

    assert response.status_code == 400
    assert "category" in response.get_json()["details"]


def test_create_ticket_missing_body(client):
    response = client.post("/api/tickets")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing request body."


def test_create_ticket_invalid_json(client):
    response = client.post("/api/tickets", data="{bad", content_type="application/json")

    assert response.status_code == 400
    assert response.get_json()["message"] == "Invalid JSON request body."


def test_get_tickets(client, valid_ticket):
    create_ticket(client, valid_ticket)

    response = client.get("/api/tickets")

    assert response.status_code == 200
    body = response.get_json()
    assert body["summary"]["total"] == 1
    assert body["summary"]["open"] == 1
    assert body["summary"]["high_critical"] == 1


def test_search_and_filter_tickets(client, valid_ticket):
    create_ticket(client, valid_ticket)

    response = client.get("/api/tickets?search=rishabh&category=Network&priority=High&status=Open")

    assert response.status_code == 200
    assert len(response.get_json()["tickets"]) == 1


def test_update_ticket(client, valid_ticket):
    ticket_id = create_ticket(client, valid_ticket).get_json()["ticket"]["_id"]

    response = client.put(
        f"/api/tickets/{ticket_id}",
        json={"status": "Resolved", "priority": "Medium", "resolution": "Updated network configuration."},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["ticket"]["status"] == "Resolved"
    assert body["ticket"]["priority"] == "Medium"
    assert body["ticket"]["resolution"] == "Updated network configuration."


def test_update_invalid_status(client, valid_ticket):
    ticket_id = create_ticket(client, valid_ticket).get_json()["ticket"]["_id"]

    response = client.put(f"/api/tickets/{ticket_id}", json={"status": "Closed"})

    assert response.status_code == 400
    assert "status" in response.get_json()["details"]


def test_update_invalid_ticket(client):
    response = client.put("/api/tickets/IT-9999", json={"status": "Resolved"})

    assert response.status_code == 404


def test_invalid_ticket_id(client):
    response = client.get("/api/tickets/abc")

    assert response.status_code == 400
