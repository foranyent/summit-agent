import json
import os
from datetime import datetime, date

# Load data files — go up one level from scripts/ to reach data/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE_DIR, "data", "orders.json")) as f:
    ORDERS_DATA = json.load(f)["orders"]

with open(os.path.join(BASE_DIR, "data", "products.json")) as f:
    PRODUCTS_DATA = json.load(f)["products"]

with open(os.path.join(BASE_DIR, "data", "policies.json")) as f:
    POLICIES_DATA = json.load(f)["policies"]


def get_order_status(order_id: str) -> dict:
    """Look up an order by order ID and return its status and details."""
    order_id = order_id.strip().upper()
    for order in ORDERS_DATA:
        if order["order_id"].upper() == order_id:
            result = {
                "found": True,
                "order_id": order["order_id"],
                "customer_name": order["customer_name"],
                "status": order["status"],
                "order_date": order["order_date"],
                "estimated_delivery": order.get("estimated_delivery"),
                "delivery_date": order.get("delivery_date"),
                "carrier": order.get("carrier"),
                "tracking_number": order.get("tracking_number"),
                "items": order["items"],
                "total": order["total"]
            }
            return result
    return {"found": False, "message": f"No order found with ID {order_id}."}


def check_return_eligibility(order_id: str) -> dict:
    """Check whether an order is eligible for return based on delivery date and policy."""
    order_id = order_id.strip().upper()
    for order in ORDERS_DATA:
        if order["order_id"].upper() == order_id:
            status = order["status"]

            if status != "delivered":
                return {
                    "eligible": False,
                    "order_id": order_id,
                    "reason": f"Order has not been delivered yet (current status: {status}). Returns can only be initiated after delivery."
                }

            delivery_date = datetime.strptime(order["delivery_date"], "%Y-%m-%d").date()
            days_since_delivery = (date.today() - delivery_date).days
            return_window = POLICIES_DATA["returns"]["window_days"]

            if days_since_delivery <= return_window:
                days_remaining = return_window - days_since_delivery
                return {
                    "eligible": True,
                    "order_id": order_id,
                    "delivery_date": order["delivery_date"],
                    "days_since_delivery": days_since_delivery,
                    "days_remaining_in_window": days_remaining,
                    "items": order["items"],
                    "return_instructions": POLICIES_DATA["returns"]["process"]
                }
            else:
                return {
                    "eligible": False,
                    "order_id": order_id,
                    "reason": f"The 30-day return window has passed. Order was delivered {days_since_delivery} days ago.",
                    "delivery_date": order["delivery_date"]
                }

    return {"found": False, "message": f"No order found with ID {order_id}."}


def search_products(query: str) -> dict:
    """Search products by name, category, or description keyword."""
    query_lower = query.lower()
    matches = []

    for product in PRODUCTS_DATA:
        searchable = (
            product["name"].lower() + " " +
            product["category"].lower() + " " +
            product.get("description", "").lower()
        )
        if any(word in searchable for word in query_lower.split()):
            matches.append({
                "product_id": product["product_id"],
                "name": product["name"],
                "category": product["category"],
                "price": product["price"],
                "in_stock": product["in_stock"],
                "description": product["description"],
                "rating": product.get("rating"),
                "review_count": product.get("review_count"),
                "restock_eta": product.get("restock_eta")
            })

    if matches:
        return {"found": True, "count": len(matches), "products": matches}
    return {"found": False, "message": f"No products found matching '{query}'."}


def escalate_to_human(reason: str, conversation_summary: str) -> dict:
    """Escalate the conversation to a human support agent and log it."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "reason": reason,
        "summary": conversation_summary
    }

    log_path = os.path.join(BASE_DIR, "escalations.json")

    # Load existing escalations or start fresh
    if os.path.exists(log_path):
        with open(log_path) as f:
            log = json.load(f)
    else:
        log = {"escalations": []}

    log["escalations"].append(log_entry)

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    return {
        "escalated": True,
        "message": "This conversation has been flagged for a human agent. Our support team is available Monday-Friday, 8am-6pm MST at support@summitoutfitters.com or 1-800-555-0198. A team member will follow up within 1 business day.",
        "timestamp": timestamp
    }


# Tool definitions for the Anthropic API
TOOL_DEFINITIONS = [
    {
        "name": "get_order_status",
        "description": "Look up a customer's order by order ID. Returns order status, tracking info, items, and delivery details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to look up, e.g. SO-1042"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "check_return_eligibility",
        "description": "Check whether an order is eligible for return based on delivery date and return policy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID to check return eligibility for"
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "search_products",
        "description": "Search the product catalog by keyword, category, or product name. Use this to answer questions about products, availability, pricing, and specs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keywords, e.g. 'rain jacket', 'tent', 'waterproof boots'"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate the conversation to a human support agent. Use this when the customer's issue cannot be resolved with available tools, when the customer is frustrated, or when the request involves something outside your capabilities.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Brief reason for escalation"
                },
                "conversation_summary": {
                    "type": "string",
                    "description": "Summary of the conversation so far for the human agent"
                }
            },
            "required": ["reason", "conversation_summary"]
        }
    }
]

# Map tool names to functions
TOOL_MAP = {
    "get_order_status": get_order_status,
    "check_return_eligibility": check_return_eligibility,
    "search_products": search_products,
    "escalate_to_human": escalate_to_human
}
