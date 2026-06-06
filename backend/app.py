import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

try:
    from .storage import get_order_by_id, get_orders, save_order, save_subscription
except ImportError:
    from storage import get_order_by_id, get_orders, save_order, save_subscription

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("PORT", 3001))

DOSA_TYPES = ["plain", "masala", "mysore", "onion", "cheese"]
ORDER_STATUSES = ["confirmed", "preparing", "in-flight", "delivered"]

ALLOWED_ORIGINS = [
    "https://chikatiyugalasri-web.github.io",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=False)


def generate_order_id():
    return f"AD-{format(int(time.time() * 1000), 'x').upper()[-6:]}"


def generate_subscription_id():
    return f"SUB-{format(int(time.time() * 1000), 'x').upper()[-6:]}"


def estimate_eta(plan: str):
    minutes = 5 if plan == "dosa-pass" else 8
    eta = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return minutes, eta.isoformat()


def validate_order(body):
    errors = []
    name = (body.get("name") or "").strip()
    phone = re.sub(r"\s", "", body.get("phone") or "")
    address = (body.get("address") or "").strip()
    dosa_type = body.get("dosaType")
    quantity = body.get("quantity")
    plan = body.get("plan")

    if not name:
        errors.append("Name is required")
    if not phone or not re.fullmatch(r"\d{10}", phone):
        errors.append("Valid 10-digit phone number is required")
    if not address:
        errors.append("Delivery address is required")
    if dosa_type not in DOSA_TYPES:
        errors.append("Invalid dosa type")
    if not quantity or quantity < 1 or quantity > 10:
        errors.append("Quantity must be 1–10")
    if plan not in ("starter", "dosa-pass"):
        errors.append("Invalid plan")

    return errors


def validate_subscription(body):
    errors = []
    name = (body.get("name") or "").strip()
    email = (body.get("email") or "").strip()
    phone = re.sub(r"\s", "", body.get("phone") or "")

    if not name:
        errors.append("Name is required")
    if not email or not re.fullmatch(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        errors.append("Valid email is required")
    if not phone or not re.fullmatch(r"\d{10}", phone):
        errors.append("Valid 10-digit phone number is required")

    return errors


def current_order_status(order):
    created = datetime.fromisoformat(order["createdAt"].replace("Z", "+00:00"))
    elapsed = (datetime.now(timezone.utc) - created).total_seconds()
    status = order["status"]

    if elapsed > 120 and status == "confirmed":
        status = "preparing"
    if elapsed > 240 and status == "preparing":
        status = "in-flight"
    if elapsed > order["etaMinutes"] * 60:
        status = "delivered"

    return status


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "AirDosa API (Python)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.post("/api/orders")
def create_order():
    body = request.get_json(silent=True) or {}
    errors = validate_order(body)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    minutes, estimated_delivery = estimate_eta(body["plan"])
    quantity = int(body["quantity"])
    plan = body["plan"]

    order = {
        "orderId": generate_order_id(),
        "name": body["name"].strip(),
        "phone": re.sub(r"\s", "", body["phone"]),
        "address": body["address"].strip(),
        "dosaType": body["dosaType"],
        "quantity": quantity,
        "plan": plan,
        "status": "confirmed",
        "statusHistory": [{"status": "confirmed", "at": datetime.now(timezone.utc).isoformat()}],
        "price": 0 if plan == "dosa-pass" else 99 * quantity,
        "etaMinutes": minutes,
        "estimatedDelivery": estimated_delivery,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    save_order(order)

    return jsonify({
        "success": True,
        "message": "Order placed! Your drone is being dispatched.",
        "order": order,
    }), 201


@app.get("/api/orders/<order_id>")
def track_order(order_id):
    order = get_order_by_id(order_id)
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    status = current_order_status(order)
    return jsonify({
        "success": True,
        "order": {**order, "status": status, "statuses": ORDER_STATUSES},
    })


@app.get("/api/orders")
def list_orders():
    orders = get_orders()
    return jsonify({"success": True, "count": len(orders), "orders": orders})


@app.post("/api/subscriptions")
def create_subscription():
    body = request.get_json(silent=True) or {}
    errors = validate_subscription(body)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    subscription = {
        "subscriptionId": generate_subscription_id(),
        "name": body["name"].strip(),
        "email": body["email"].strip(),
        "phone": re.sub(r"\s", "", body["phone"]),
        "plan": "dosa-pass",
        "price": 499,
        "status": "active",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }

    save_subscription(subscription)

    return jsonify({
        "success": True,
        "message": "Welcome to Dosa Pass! Unlimited crispy goodness awaits.",
        "subscription": subscription,
    }), 201


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_frontend(path):
    if path.startswith("api/"):
        return jsonify({"success": False, "message": "Not found"}), 404
    target = ROOT / path
    if target.is_file():
        return send_from_directory(ROOT, path)
    return send_from_directory(ROOT, "index.html")


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    print(f"AirDosa API (Python) running at http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=debug)
