import json
from pathlib import Path

try:
    from .supabase_client import get_client, is_configured
except ImportError:
    from supabase_client import get_client, is_configured

DATA_DIR = Path(__file__).parent / "data"


def storage_mode():
    return "supabase" if is_configured() else "json"


def _row_to_order(row):
    return {
        "orderId": row["order_id"],
        "name": row["name"],
        "phone": row["phone"],
        "address": row["address"],
        "dosaType": row["dosa_type"],
        "quantity": row["quantity"],
        "plan": row["plan"],
        "status": row["status"],
        "statusHistory": row.get("status_history") or [],
        "price": row["price"],
        "etaMinutes": row["eta_minutes"],
        "estimatedDelivery": row["estimated_delivery"],
        "createdAt": row["created_at"],
    }


def _row_to_subscription(row):
    return {
        "subscriptionId": row["subscription_id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "plan": row["plan"],
        "price": row["price"],
        "status": row["status"],
        "createdAt": row["created_at"],
    }


def _order_to_row(order):
    return {
        "order_id": order["orderId"],
        "name": order["name"],
        "phone": order["phone"],
        "address": order["address"],
        "dosa_type": order["dosaType"],
        "quantity": order["quantity"],
        "plan": order["plan"],
        "status": order["status"],
        "status_history": order.get("statusHistory", []),
        "price": order["price"],
        "eta_minutes": order["etaMinutes"],
        "estimated_delivery": order["estimatedDelivery"],
        "created_at": order["createdAt"],
    }


def _subscription_to_row(subscription):
    return {
        "subscription_id": subscription["subscriptionId"],
        "name": subscription["name"],
        "email": subscription["email"],
        "phone": subscription["phone"],
        "plan": subscription["plan"],
        "price": subscription["price"],
        "status": subscription["status"],
        "created_at": subscription["createdAt"],
    }


# ── JSON fallback (local dev without Supabase) ──

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(filename: str, fallback=None):
    if fallback is None:
        fallback = []
    _ensure_data_dir()
    path = DATA_DIR / filename
    if not path.exists():
        return fallback
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_json(filename: str, data):
    _ensure_data_dir()
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── Public API ──

def get_orders():
    client = get_client()
    if client:
        result = client.table("orders").select("*").order("created_at", desc=True).execute()
        return [_row_to_order(row) for row in (result.data or [])]
    return _read_json("orders.json", [])


def save_order(order):
    client = get_client()
    if client:
        row = _order_to_row(order)
        result = client.table("orders").insert(row).execute()
        if result.data:
            return _row_to_order(result.data[0])
        return order

    orders = _read_json("orders.json", [])
    orders.append(order)
    _write_json("orders.json", orders)
    return order


def get_order_by_id(order_id: str):
    order_id = order_id.upper()
    client = get_client()
    if client:
        result = (
            client.table("orders")
            .select("*")
            .eq("order_id", order_id)
            .limit(1)
            .execute()
        )
        if result.data:
            return _row_to_order(result.data[0])
        return None

    orders = _read_json("orders.json", [])
    return next((o for o in orders if o["orderId"] == order_id), None)


def save_subscription(subscription):
    client = get_client()
    if client:
        row = _subscription_to_row(subscription)
        result = client.table("subscriptions").insert(row).execute()
        if result.data:
            return _row_to_subscription(result.data[0])
        return subscription

    subscriptions = _read_json("subscriptions.json", [])
    subscriptions.append(subscription)
    _write_json("subscriptions.json", subscriptions)
    return subscription
