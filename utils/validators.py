import re

ALLOWED_CATEGORIES = {"Hardware", "Software", "Network", "Account", "Other"}
ALLOWED_PRIORITIES = {"Low", "Medium", "High", "Critical"}
ALLOWED_STATUSES = {"Open", "In Progress", "Resolved"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_ticket_payload(data):
    errors = {}
    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object."}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    category = str(data.get("category", "")).strip()
    priority = str(data.get("priority", "")).strip()
    description = str(data.get("description", "")).strip()

    if len(name) < 2:
        errors["name"] = "Name is required and must be at least 2 characters."
    if not EMAIL_PATTERN.match(email):
        errors["email"] = "A valid email address is required."
    if category not in ALLOWED_CATEGORIES:
        errors["category"] = f"Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}."
    if priority not in ALLOWED_PRIORITIES:
        errors["priority"] = f"Priority must be one of: {', '.join(sorted(ALLOWED_PRIORITIES))}."
    if len(description) < 10:
        errors["description"] = "Description is required and must be at least 10 characters."
    return errors


def validate_update_payload(data):
    errors = {}
    if not isinstance(data, dict):
        return {"body": "Request body must be a JSON object."}

    allowed_fields = {"status", "priority", "resolution"}
    unknown_fields = set(data) - allowed_fields
    if unknown_fields:
        errors["fields"] = f"Unsupported fields: {', '.join(sorted(unknown_fields))}."

    if "status" in data and data["status"] not in ALLOWED_STATUSES:
        errors["status"] = f"Status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}."
    if "priority" in data and data["priority"] not in ALLOWED_PRIORITIES:
        errors["priority"] = f"Priority must be one of: {', '.join(sorted(ALLOWED_PRIORITIES))}."
    if "resolution" in data and not isinstance(data["resolution"], str):
        errors["resolution"] = "Resolution must be text."
    if not any(field in data for field in allowed_fields):
        errors["body"] = "At least one updatable field is required."
    return errors


def is_valid_ticket_id(ticket_id):
    return bool(re.fullmatch(r"IT-\d{4,}", ticket_id or ""))
