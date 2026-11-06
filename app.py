from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from datetime import date, datetime

app = Flask(__name__)
app.secret_key = "fintrack-secret-key"
DATABASE = "expenses.db"

EXPENSE_CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills",
    "Education", "Entertainment", "Health", "Other"
]

INCOME_CATEGORIES = [
    "Salary", "Freelance", "Allowance", "Investment", "Other"
]

ALL_CATEGORIES = list(dict.fromkeys(EXPENSE_CATEGORIES + INCOME_CATEGORIES))
TRANSACTION_TYPES = ["Income", "Expense"]


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK(transaction_type IN ('Income', 'Expense')),
                transaction_date TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS migration_log (
                migration_name TEXT PRIMARY KEY
            )
        """)

        # Migrate existing expenses from the previous project version.
        already_migrated = conn.execute(
            "SELECT 1 FROM migration_log WHERE migration_name = ?",
            ("old_expenses_to_transactions",)
        ).fetchone()

        if not already_migrated:
            old_table = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name = 'expenses'
            """).fetchone()

            if old_table:
                columns = {
                    row["name"]
                    for row in conn.execute(
                        "PRAGMA table_info(expenses)"
                    ).fetchall()
                }

                required = {"id", "title", "amount", "category", "expense_date"}

                if required.issubset(columns):
                    conn.execute("""
                        INSERT INTO transactions
                            (id, title, amount, category,
                             transaction_type, transaction_date)
                        SELECT id, title, amount, category,
                               'Expense', expense_date
                        FROM expenses
                    """)

            conn.execute("""
                INSERT INTO migration_log (migration_name)
                VALUES (?)
            """, ("old_expenses_to_transactions",))


initialize_db()


# ---------------- VALIDATION ----------------


def validate_transaction(data):

    if data is None or not hasattr(data, "get"):
        return None, "Invalid transaction data"

    title = data.get("title")
    amount = data.get("amount")
    category = data.get("category")
    transaction_type = data.get("transaction_type")
    transaction_date = data.get("transaction_date")

    # Validate title
    if not isinstance(title, str) or not title.strip():
        return None, "Title is required"

    # Validate amount
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return None, "Amount must be a valid number"

    if amount <= 0 or amount == float("inf") or amount != amount:
        return None, "Amount must be greater than zero"

    # Validate transaction type
    if transaction_type not in TRANSACTION_TYPES:
        return None, "Select a valid transaction type"

    # Validate category
    allowed_categories = (
        INCOME_CATEGORIES
        if transaction_type == "Income"
        else EXPENSE_CATEGORIES
    )

    if category not in allowed_categories:
        return None, "Select a valid category for this transaction type"

    # Validate date
    if not isinstance(transaction_date, str):
        return None, "Date is required"

    try:
        parsed_date = datetime.strptime(
            transaction_date, "%Y-%m-%d"
        ).date()

        if parsed_date.isoformat() != transaction_date:
            return None, "Invalid date format"

    except ValueError:
        return None, "Enter a valid date"

    if parsed_date.year < 1900:
        return None, "Enter a valid date"

    if parsed_date > date.today():
        return None, "Future dates are not allowed"

    return {
        "title": title.strip(),
        "amount": amount,
        "category": category,
        "transaction_type": transaction_type,
        "transaction_date": transaction_date
    }, None

# ---------------- DASHBOARD ----------------

@app.route("/")
def home():
    today = date.today()
    month_start = today.replace(day=1).isoformat()

    with get_db() as conn:
        income = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Income'
        """).fetchone()[0]

        expenses = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Expense'
        """).fetchone()[0]

        monthly_expenses = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Expense'
              AND transaction_date BETWEEN ? AND ?
        """, (month_start, today.isoformat())).fetchone()[0]

        today_expenses = conn.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE transaction_type = 'Expense'
              AND transaction_date = ?
        """, (today.isoformat(),)).fetchone()[0]

        count = conn.execute("""
            SELECT COUNT(*) FROM transactions
        """).fetchone()[0]

        recent = conn.execute("""
            SELECT * FROM transactions
            ORDER BY transaction_date DESC, id DESC
            LIMIT 5
        """).fetchall()

        category_totals = conn.execute("""
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE transaction_type = 'Expense'
            GROUP BY category
        """).fetchall()

    return render_template(
        "index.html",
        income=income,
        expenses=expenses,
        savings=income - expenses,
        monthly_expenses=monthly_expenses,
        today_expenses=today_expenses,
        count=count,
        recent=recent,
        category_totals=category_totals
    )


# ---------------- TRANSACTIONS PAGE ----------------

@app.route("/transactions")
def transactions():
    search = request.args.get("q", "").strip()
    transaction_type = request.args.get("type", "").strip()
    category = request.args.get("category", "").strip()

    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if transaction_type in TRANSACTION_TYPES:
        query += " AND transaction_type = ?"
        params.append(transaction_type)

    if category in ALL_CATEGORIES:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY transaction_date DESC, id DESC"

    with get_db() as conn:
        records = conn.execute(query, params).fetchall()

    return render_template(
        "transactions.html",
        records=records,
        search=search,
        selected_type=transaction_type,
        selected_category=category,
        categories=ALL_CATEGORIES,
        types=TRANSACTION_TYPES
    )


# ---------------- ADD TRANSACTION ----------------

@app.route("/add", methods=["POST"])
def add_transaction():
    data, error = validate_transaction(request.form)

    if error:
        flash(error, "error")
        return redirect(url_for("home"))

    with get_db() as conn:
        conn.execute("""
            INSERT INTO transactions
            (title, amount, category, transaction_type, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["title"],
            data["amount"],
            data["category"],
            data["transaction_type"],
            data["transaction_date"]
        ))

    flash("Transaction added successfully!", "success")
    return redirect(url_for("home"))
# ---------------- EDIT TRANSACTION ----------------

@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    with get_db() as conn:
        record = conn.execute("""
            SELECT * FROM transactions WHERE id = ?
        """, (transaction_id,)).fetchone()

        if record is None:
            return "Transaction not found", 404

        if request.method == "POST":
            data, error = validate_transaction(request.form)

            if error:
                return error, 400

            conn.execute("""
                UPDATE transactions
                SET title = ?, amount = ?, category = ?,
                    transaction_type = ?, transaction_date = ?
                WHERE id = ?
            """, (
                data["title"],
                data["amount"],
                data["category"],
                data["transaction_type"],
                data["transaction_date"],
                transaction_id
            ))

            return redirect(url_for("transactions"))

    return render_template(
        "edit.html",
        record=record,
        income_categories=INCOME_CATEGORIES,
        expense_categories=EXPENSE_CATEGORIES
    )


# ---------------- DELETE TRANSACTION ----------------

@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

    return redirect(url_for("transactions"))


# ---------------- REST API ----------------

@app.route("/api/transactions", methods=["GET", "POST"])
def api_transactions():

    if request.method == "GET":
        transaction_type = request.args.get("type", "")
        category = request.args.get("category", "")

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if transaction_type in TRANSACTION_TYPES:
            query += " AND transaction_type = ?"
            params.append(transaction_type)

        if category in ALL_CATEGORIES:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY transaction_date DESC, id DESC"

        with get_db() as conn:
            records = conn.execute(query, params).fetchall()

        return jsonify([dict(row) for row in records])

    data, error = validate_transaction(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO transactions
            (title, amount, category, transaction_type, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["title"],
            data["amount"],
            data["category"],
            data["transaction_type"],
            data["transaction_date"]
        ))

        record = conn.execute(
            "SELECT * FROM transactions WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()

    return jsonify(dict(record)), 201


@app.route("/api/transactions/<int:transaction_id>",
           methods=["GET", "PUT", "DELETE"])
def api_transaction_detail(transaction_id):

    with get_db() as conn:
        record = conn.execute(
            "SELECT * FROM transactions WHERE id = ?",
            (transaction_id,)
        ).fetchone()

        if record is None:
            return jsonify({"error": "Transaction not found"}), 404
        if request.method == "GET":
            return jsonify(dict(record))
        if request.method == "DELETE":
            conn.execute(
                "DELETE FROM transactions WHERE id = ?",
                (transaction_id,)
            )
            return jsonify({"message": "Transaction deleted successfully"})
        data, error = validate_transaction(
            request.get_json(silent=True)
        )
        if error:
            return jsonify({"error": error}), 400
        conn.execute("""
            UPDATE transactions
            SET title = ?, amount = ?, category = ?,
                transaction_type = ?, transaction_date = ?
            WHERE id = ?
        """, (
            data["title"],
            data["amount"],
            data["category"],
            data["transaction_type"],
            data["transaction_date"],
            transaction_id
        ))
        updated = conn.execute(
            "SELECT * FROM transactions WHERE id = ?",
            (transaction_id,)
        ).fetchone()
    return jsonify(dict(updated))
# ---------------- RUN APPLICATION ----------------
if __name__ == "__main__":
    app.run(debug=True)
