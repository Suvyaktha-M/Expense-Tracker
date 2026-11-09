# 💰 Expense Tracker

A full-stack Expense Tracker web application built using Python, Flask, HTML, CSS, and SQLite. It helps users manage their income and expenses, organize transactions by category, and monitor their financial summaries through a dashboard.

## ✨ Features

- **Income and Expense Management:** Add, edit, and delete financial transactions.
- **Dashboard:** View total income, total expenses, and current net savings.
- **Transaction History:** View all transactions with category and transaction-type badges.
- **Search and Filtering:** Search transactions by title and filter by type and category.
- **Input Validation:** Client-side and server-side validation for transaction details.
- **Data Persistence:** Store transaction records in an SQLite database.
- **Expense Summaries:** View monthly expenses, today's expenses, and category-wise expense totals.
- **Responsive Design:** Interface designed for desktop and mobile screens.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| HTML5 | Page structure |
| CSS3 | Styling and responsive design |
| Python | Backend programming |
| Flask | Web framework and REST API |
| SQLite | Database management |

## 📁 Project Structure

```text
Expense-Tracker/
│
├── app.py
├── expenses.db
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   └── style.css
│
└── templates/
    ├── index.html
    ├── transactions.html
    └── edit.html
```

**Note:** `expenses.db` is generated automatically when the application runs for the first time. It is not required to be uploaded to GitHub.

## ⚙️ Installation and Setup

### Prerequisites
- Python 3.x
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Suvyaktha-M/Expense-Tracker.git
```

### 2. Navigate to the project directory

```bash
cd Expense-Tracker
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Open the following URL in your browser:

```text
http://127.0.0.1:5000/
```

## 🗄️ Database Model

The application uses SQLite with a `transactions` table.

| Column | Data Type | Description |
|---|---|---|
| id | INTEGER | Primary key, auto-incremented |
| title | TEXT | Transaction title |
| amount | REAL | Transaction amount (must be positive) |
| category | TEXT | Transaction category |
| transaction_type | TEXT | Income or Expense |
| transaction_date | TEXT | Transaction date in YYYY-MM-DD format |

The database also contains a `migration_log` table to track migration of records from the earlier expenses table.

## 🔌 REST API Documentation

Base URL:

```text
http://127.0.0.1:5000
```

### API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/transactions` | Retrieve all transactions |
| POST | `/api/transactions` | Create a transaction |
| GET | `/api/transactions/<id>` | Retrieve a transaction by ID |
| PUT | `/api/transactions/<id>` | Update a transaction |
| DELETE | `/api/transactions/<id>` | Delete a transaction |

### Sample JSON Request

Use this JSON format when creating or updating a transaction:

```json
{
  "title": "Monthly Salary",
  "amount": 25000,
  "category": "Salary",
  "transaction_type": "Income",
  "transaction_date": "2026-11-05"
}
```

### Response Status Codes

| Status Code | Description |
|---|---|
| 200 | Request successful |
| 201 | Transaction created successfully |
| 400 | Invalid transaction data |
| 404 | Transaction not found |

The GET transactions endpoint also supports filtering by transaction type and category using query parameters.

Example:

```text
/api/transactions?type=Expense&category=Food
```

## ✅ Validation

The application validates transaction details on both the client and server sides.

- Transaction title cannot be empty.
- Amount must be a valid positive number.
- Transaction type must be Income or Expense.
- Category must match the selected transaction type.
- Date must be valid and cannot be in the future.
- Invalid API requests are rejected with appropriate error responses.

## 📌 Project Objective

This project focuses on full-stack development, REST API integration, data validation, database persistence, and responsive user interface design.
