from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest

from utils.validators import validate_ticket_payload, validate_update_payload, is_valid_ticket_id

ticket_bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")


def json_body():
    if not request.data:
        raise BadRequest("Missing request body.")
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Invalid JSON request body.")
    return data


def validation_error(errors):
    return jsonify({"error": "Validation failed", "details": errors}), 400


@ticket_bp.post("")
def create_ticket():
    data = json_body()
    errors = validate_ticket_payload(data)
    if errors:
        return validation_error(errors)
    ticket = current_app.ticket_service.create_ticket(data)
    return jsonify({"message": "Ticket created successfully", "ticket": ticket}), 201


@ticket_bp.get("")
def get_tickets():
    tickets = current_app.ticket_service.list_tickets(
        search=request.args.get("search", "").strip() or None,
        category=request.args.get("category") or None,
        priority=request.args.get("priority") or None,
        status=request.args.get("status") or None,
    )
    summary = {
        "total": len(tickets),
        "open": sum(t["status"] == "Open" for t in tickets),
        "in_progress": sum(t["status"] == "In Progress" for t in tickets),
        "resolved": sum(t["status"] == "Resolved" for t in tickets),
        "high_critical": sum(t["priority"] in {"High", "Critical"} for t in tickets),
    }
    return jsonify({"tickets": tickets, "summary": summary})


@ticket_bp.get("/<ticket_id>")
def get_ticket(ticket_id):
    if not is_valid_ticket_id(ticket_id):
        return jsonify({"error": "Invalid ticket ID"}), 400
    ticket = current_app.ticket_service.get_ticket(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({"ticket": ticket})


@ticket_bp.put("/<ticket_id>")
def update_ticket(ticket_id):
    if not is_valid_ticket_id(ticket_id):
        return jsonify({"error": "Invalid ticket ID"}), 400
    data = json_body()
    errors = validate_update_payload(data)
    if errors:
        return validation_error(errors)
    ticket = current_app.ticket_service.update_ticket(ticket_id, data)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({"message": "Ticket updated successfully", "ticket": ticket})


@ticket_bp.delete("/<ticket_id>")
def delete_ticket(ticket_id):
    if not is_valid_ticket_id(ticket_id):
        return jsonify({"error": "Invalid ticket ID"}), 400
    deleted = current_app.ticket_service.delete_ticket(ticket_id)
    if not deleted:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({"message": "Ticket deleted successfully"})
