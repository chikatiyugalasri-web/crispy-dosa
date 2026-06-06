import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


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


def get_orders():
    return _read_json("orders.json", [])


def save_order(order):
    orders = get_orders()
    orders.append(order)
    _write_json("orders.json", orders)
    return order


def get_order_by_id(order_id: str):
    orders = get_orders()
    order_id = order_id.upper()
    return next((o for o in orders if o["orderId"] == order_id), None)


def save_subscription(subscription):
    subscriptions = _read_json("subscriptions.json", [])
    subscriptions.append(subscription)
    _write_json("subscriptions.json", subscriptions)
    return subscription
