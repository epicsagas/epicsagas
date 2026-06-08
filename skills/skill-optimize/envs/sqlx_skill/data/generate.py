#!/usr/bin/env python3
"""Generate sqlx benchmark splits at TARGET_DIR/.skillopt/."""

import json, os, random

random.seed(42)

items = []

# ── SELECT (20) ──────────────────────────────────────────────────────────
items += [
    {
        "id": "sel-001",
        "task_type": "query",
        "input": "Show me all users from mysql_main",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM users",
            "params": [],
            "connection": "mysql_main",
        },
    },
    {
        "id": "sel-002",
        "task_type": "query",
        "input": "Get active users from the main MySQL database",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM users WHERE status = ?",
            "params": ["active"],
            "connection": "mysql_main",
        },
    },
    {
        "id": "sel-003",
        "task_type": "query",
        "input": "Show last 10 orders from postgres",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?",
            "params": [10],
            "connection": "postgres",
        },
    },
    {
        "id": "sel-004",
        "task_type": "query",
        "input": "Find products priced over 50000 in the shop database",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM products WHERE price > ?",
            "params": [50000],
            "connection": "shop",
        },
    },
    {
        "id": "sel-005",
        "task_type": "query",
        "input": "Count total orders in postgres",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT COUNT(*) FROM orders",
            "params": [],
            "connection": "postgres",
        },
    },
    {
        "id": "sel-006",
        "task_type": "query",
        "input": "Get users who signed up this month from mysql_main",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM users WHERE created_at >= ?",
            "params": ["2026-06-01"],
            "connection": "mysql_main",
        },
    },
    {
        "id": "sel-007",
        "task_type": "query",
        "input": "Search for orders containing 'laptop' in item names from shop",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM orders WHERE item_name LIKE ?",
            "params": ["%laptop%"],
            "connection": "shop",
        },
    },
    {
        "id": "sel-008",
        "task_type": "query",
        "input": "List the top 5 customers by total spend in postgres",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM customers ORDER BY total_spend DESC LIMIT ?",
            "params": [5],
            "connection": "postgres",
        },
    },
    {
        "id": "sel-009",
        "task_type": "query",
        "input": "Find inactive sessions in sqlite_cache older than 7 days",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM sessions WHERE status = ? AND updated_at < ?",
            "params": ["inactive", "2026-06-02"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "sel-010",
        "task_type": "query",
        "input": "Get product categories and their counts from shop",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT category, COUNT(*) FROM products GROUP BY category",
            "params": [],
            "connection": "shop",
        },
    },
    {
        "id": "sel-011",
        "task_type": "query",
        "input": "Show all admins from mysql_main",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM users WHERE role = ?",
            "params": ["admin"],
            "connection": "mysql_main",
        },
    },
    {
        "id": "sel-012",
        "task_type": "query",
        "input": "Find duplicate emails in postgres users table",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > ?",
            "params": [1],
            "connection": "postgres",
        },
    },
    {
        "id": "sel-013",
        "task_type": "query",
        "input": "Get recent log entries from sqlite_cache",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM logs ORDER BY created_at DESC",
            "params": [],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "sel-014",
        "task_type": "query",
        "input": "Average order value in shop database",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT AVG(total) FROM orders",
            "params": [],
            "connection": "shop",
        },
    },
    {
        "id": "sel-015",
        "task_type": "query",
        "input": "Users with pending status in mysql_main who registered before June",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM users WHERE status = ? AND created_at < ?",
            "params": ["pending", "2026-06-01"],
            "connection": "mysql_main",
        },
    },
    {
        "id": "sel-016",
        "task_type": "query",
        "input": "Join orders with customers from postgres to get customer names for recent orders",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id ORDER BY o.created_at DESC",
            "params": [],
            "connection": "postgres",
        },
    },
    {
        "id": "sel-017",
        "task_type": "query",
        "input": "Check if product SKU-1234 exists in shop",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM products WHERE sku = ?",
            "params": ["SKU-1234"],
            "connection": "shop",
        },
    },
    {
        "id": "sel-018",
        "task_type": "query",
        "input": "Sum of all payments this week from postgres",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT SUM(amount) FROM payments WHERE paid_at >= ?",
            "params": ["2026-06-02"],
            "connection": "postgres",
        },
    },
    {
        "id": "sel-019",
        "task_type": "query",
        "input": "Get cache entries expiring soon from sqlite_cache",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT * FROM cache WHERE expires_at <= ?",
            "params": ["2026-06-10"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "sel-020",
        "task_type": "query",
        "input": "Monthly revenue report from shop for 2026",
        "expected_tool": "db_query",
        "expected_params": {
            "query": "SELECT MONTH(created_at) as month, SUM(total) FROM orders WHERE created_at >= ? GROUP BY month",
            "params": ["2026-01-01"],
            "connection": "shop",
        },
    },
]

# ── INSERT (10) ──────────────────────────────────────────────────────────
items += [
    {
        "id": "ins-001",
        "task_type": "insert",
        "input": "Add user Alice to mysql_main",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO users (name) VALUES (?)",
            "params": ["Alice"],
            "connection": "mysql_main",
        },
    },
    {
        "id": "ins-002",
        "task_type": "insert",
        "input": "Insert a new order for customer_id 42 with total 150000 into shop database",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO orders (customer_id, total) VALUES (?, ?)",
            "params": [42, 150000],
            "connection": "shop",
        },
    },
    {
        "id": "ins-003",
        "task_type": "insert",
        "input": "Add log entry 'user login' to sqlite_cache",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO logs (message) VALUES (?)",
            "params": ["user login"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "ins-004",
        "task_type": "insert",
        "input": "Create new product 'Widget' with price 9900 and category 'tools' in shop",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
            "params": ["Widget", 9900, "tools"],
            "connection": "shop",
        },
    },
    {
        "id": "ins-005",
        "task_type": "insert",
        "input": "Insert admin user Bob with email bob@example.com into mysql_main",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO users (name, email, role) VALUES (?, ?, ?)",
            "params": ["Bob", "bob@example.com", "admin"],
            "connection": "mysql_main",
        },
    },
    {
        "id": "ins-006",
        "task_type": "insert",
        "input": "Add payment of 50000 for order 7 in postgres",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO payments (order_id, amount) VALUES (?, ?)",
            "params": [7, 50000],
            "connection": "postgres",
        },
    },
    {
        "id": "ins-007",
        "task_type": "insert",
        "input": "Store session token abc123 for user 5 in sqlite_cache",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO sessions (user_id, token) VALUES (?, ?)",
            "params": [5, "abc123"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "ins-008",
        "task_type": "insert",
        "input": "Add customer Charlie with email charlie@test.com to shop",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO customers (name, email) VALUES (?, ?)",
            "params": ["Charlie", "charlie@test.com"],
            "connection": "shop",
        },
    },
    {
        "id": "ins-009",
        "task_type": "insert",
        "input": "Insert a new order item: product_id 3, quantity 2, order_id 15 into postgres",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            "params": [15, 3, 2],
            "connection": "postgres",
        },
    },
    {
        "id": "ins-010",
        "task_type": "insert",
        "input": "Add cache key 'homepage' with value 'rendered_html' to sqlite_cache",
        "expected_tool": "db_insert",
        "expected_params": {
            "query": "INSERT INTO cache (key, value) VALUES (?, ?)",
            "params": ["homepage", "rendered_html"],
            "connection": "sqlite_cache",
        },
    },
]

# ── UPDATE (10) ──────────────────────────────────────────────────────────
items += [
    {
        "id": "upd-001",
        "task_type": "update",
        "input": "Update user id=5 to name Jane in postgres",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE users SET name = ? WHERE id = ?",
            "params": ["Jane", 5],
            "connection": "postgres",
        },
    },
    {
        "id": "upd-002",
        "task_type": "update",
        "input": "Set status to 'active' for user id 12 in mysql_main",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE users SET status = ? WHERE id = ?",
            "params": ["active", 12],
            "connection": "mysql_main",
        },
    },
    {
        "id": "upd-003",
        "task_type": "update",
        "input": "Change price of product id 8 to 25000 in shop",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE products SET price = ? WHERE id = ?",
            "params": [25000, 8],
            "connection": "shop",
        },
    },
    {
        "id": "upd-004",
        "task_type": "update",
        "input": "Mark order id 3 as 'shipped' in postgres",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE orders SET status = ? WHERE id = ?",
            "params": ["shipped", 3],
            "connection": "postgres",
        },
    },
    {
        "id": "upd-005",
        "task_type": "update",
        "input": "Update email for user id 7 to new@example.com in mysql_main",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE users SET email = ? WHERE id = ?",
            "params": ["new@example.com", 7],
            "connection": "mysql_main",
        },
    },
    {
        "id": "upd-006",
        "task_type": "update",
        "input": "Set all inactive sessions to expired in sqlite_cache",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE sessions SET status = ? WHERE status = ?",
            "params": ["expired", "inactive"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "upd-007",
        "task_type": "update",
        "input": "Increase price by 10% for all products in category 'electronics' in shop",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE products SET price = price * ? WHERE category = ?",
            "params": [1.1, "electronics"],
            "connection": "shop",
        },
    },
    {
        "id": "upd-008",
        "task_type": "update",
        "input": "Update customer id 2 total_spend to 500000 in shop",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE customers SET total_spend = ? WHERE id = ?",
            "params": [500000, 2],
            "connection": "shop",
        },
    },
    {
        "id": "upd-009",
        "task_type": "update",
        "input": "Set role to 'moderator' for user id 10 in mysql_main",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE users SET role = ? WHERE id = ?",
            "params": ["moderator", 10],
            "connection": "mysql_main",
        },
    },
    {
        "id": "upd-010",
        "task_type": "update",
        "input": "Renew cache key 'homepage' expiration to 2026-07-01 in sqlite_cache",
        "expected_tool": "db_update",
        "expected_params": {
            "query": "UPDATE cache SET expires_at = ? WHERE key = ?",
            "params": ["2026-07-01", "homepage"],
            "connection": "sqlite_cache",
        },
    },
]

# ── DELETE (10) ──────────────────────────────────────────────────────────
items += [
    {
        "id": "del-001",
        "task_type": "delete",
        "input": "Delete order id=10 from mydb",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM orders WHERE id = ?",
            "params": [10],
            "connection": "mydb",
        },
    },
    {
        "id": "del-002",
        "task_type": "delete",
        "input": "Remove user id 99 from mysql_main",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM users WHERE id = ?",
            "params": [99],
            "connection": "mysql_main",
        },
    },
    {
        "id": "del-003",
        "task_type": "delete",
        "input": "Delete expired sessions from sqlite_cache",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM sessions WHERE status = ?",
            "params": ["expired"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "del-004",
        "task_type": "delete",
        "input": "Remove product id 5 from shop database",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM products WHERE id = ?",
            "params": [5],
            "connection": "shop",
        },
    },
    {
        "id": "del-005",
        "task_type": "delete",
        "input": "Delete all logs older than 30 days from sqlite_cache",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM logs WHERE created_at < ?",
            "params": ["2026-05-10"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "del-006",
        "task_type": "delete",
        "input": "Remove cancelled orders from postgres",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM orders WHERE status = ?",
            "params": ["cancelled"],
            "connection": "postgres",
        },
    },
    {
        "id": "del-007",
        "task_type": "delete",
        "input": "Delete payment id 20 from postgres",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM payments WHERE id = ?",
            "params": [20],
            "connection": "postgres",
        },
    },
    {
        "id": "del-008",
        "task_type": "delete",
        "input": "Remove cache entry with key 'temp_data' from sqlite_cache",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM cache WHERE key = ?",
            "params": ["temp_data"],
            "connection": "sqlite_cache",
        },
    },
    {
        "id": "del-009",
        "task_type": "delete",
        "input": "Delete customer id 15 from shop",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM customers WHERE id = ?",
            "params": [15],
            "connection": "shop",
        },
    },
    {
        "id": "del-010",
        "task_type": "delete",
        "input": "Remove pending users who registered before 2025 from mysql_main",
        "expected_tool": "db_delete",
        "expected_params": {
            "query": "DELETE FROM users WHERE status = ? AND created_at < ?",
            "params": ["pending", "2025-01-01"],
            "connection": "mysql_main",
        },
    },
]

# ── Metadata (10) ────────────────────────────────────────────────────────
items += [
    {
        "id": "meta-001",
        "task_type": "metadata",
        "input": "List tables in sqlite_cache",
        "expected_tool": "db_list_tables",
        "expected_params": {"connection": "sqlite_cache"},
    },
    {
        "id": "meta-002",
        "task_type": "metadata",
        "input": "Describe users table in mysql_main",
        "expected_tool": "db_describe_table",
        "expected_params": {"table": "users", "connection": "mysql_main"},
    },
    {
        "id": "meta-003",
        "task_type": "metadata",
        "input": "Show available database connections",
        "expected_tool": "db_list_connections",
        "expected_params": {},
    },
    {
        "id": "meta-004",
        "task_type": "metadata",
        "input": "Check health of postgres connection",
        "expected_tool": "db_health_check",
        "expected_params": {"connection": "postgres"},
    },
    {
        "id": "meta-005",
        "task_type": "metadata",
        "input": "What columns does the orders table have in shop?",
        "expected_tool": "db_describe_table",
        "expected_params": {"table": "orders", "connection": "shop"},
    },
    {
        "id": "meta-006",
        "task_type": "metadata",
        "input": "List all tables in the postgres database",
        "expected_tool": "db_list_tables",
        "expected_params": {"connection": "postgres"},
    },
    {
        "id": "meta-007",
        "task_type": "metadata",
        "input": "Describe products schema in shop",
        "expected_tool": "db_describe_table",
        "expected_params": {"table": "products", "connection": "shop"},
    },
    {
        "id": "meta-008",
        "task_type": "metadata",
        "input": "Is mysql_main database responding?",
        "expected_tool": "db_health_check",
        "expected_params": {"connection": "mysql_main"},
    },
    {
        "id": "meta-009",
        "task_type": "metadata",
        "input": "Show me the schema of sessions in sqlite_cache",
        "expected_tool": "db_describe_table",
        "expected_params": {"table": "sessions", "connection": "sqlite_cache"},
    },
    {
        "id": "meta-010",
        "task_type": "metadata",
        "input": "What tables exist in shop database?",
        "expected_tool": "db_list_tables",
        "expected_params": {"connection": "shop"},
    },
]

# ── Shuffle & split 60/20/20 ─────────────────────────────────────────────
random.shuffle(items)
n = len(items)
train, val, test = (
    items[: int(n * 0.6)],
    items[int(n * 0.6) : int(n * 0.8)],
    items[int(n * 0.8) :],
)

base = os.environ.get("SPLIT_DIR", "")
if not base:
    base = os.path.join(os.path.dirname(__file__), "split")
os.makedirs(base, exist_ok=True)

for name, split in [("train", train), ("val", val), ("test", test)]:
    split_subdir = os.path.join(base, name)
    os.makedirs(split_subdir, exist_ok=True)
    with open(os.path.join(split_subdir, "items.json"), "w") as f:
        json.dump(split, f, indent=2, ensure_ascii=False)
    print(f"  {name}: {len(split)} items")

print(f"  Total: {n}")
