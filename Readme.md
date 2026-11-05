# Expense Tracker – FinTrack

FinTrack is a full-stack personal expense management application built using Python, Flask, SQLite, HTML, and CSS. It allows users to record income and expenses, monitor their financial balance, and manage transaction history.

## Features

### Financial Dashboard
- Total income calculation
- Total expenses calculation
- Current net savings calculation
- Monthly and daily expense summaries
- Category-wise expense breakdown
- Recent transaction overview

### Transaction Management
- Add income and expense records
- View transaction history
- Edit existing transactions
- Delete transactions
- Search transactions by title
- Filter by transaction type and category
- Display transaction categories using badges

### Validation and Data Persistence
- Client-side validation using HTML form attributes
- Server-side validation using Flask
- Positive amount validation
- Transaction type and category validation
- Date format validation
- SQLite database persistence across server restarts

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend application logic |
| Flask | Web framework and REST API |
| SQLite | Persistent database |
| HTML | Frontend structure and forms |
| CSS | Styling and responsive layout |

## Project Structure

```text
Expense Tracker/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   └── style.css
└── templates/
    ├── index.html
    ├── transactions.html
    └── edit.html
```

The SQLite database is generated automatically when the application starts. Existing expense records from the previous database structure are migrated into the unified transactions table.

## Installation and Setup

### Prerequisites
- Python 3
- Git (for cloning the repository)

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd "Expense Tracker"
```

### 2. Create a Virtual Environment

```bash
py -m venv venv
```

### 3. Activate the Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

Open the application at:

`http://127.0.0.1:5000`

## REST API Documentation

Base URL: `http://127.0.0.1:5000`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/transactions` | Retrieve all transactions |
| GET | `/api/transactions?type=Income` | Filter by transaction type |
| GET | `/api/transactions?category=Food` | Filter by category |
| GET | `/api/transactions/<id>` | Retrieve a specific transaction |
| POST | `/api/transactions` | Create a transaction |
| PUT | `/api/transactions/<id>` | Update a transaction |
| DELETE | `/api/transactions/<id>` | Delete a transaction |

### Example JSON Request

POST `/api/transactions`

```json
{
  "title": "Monthly Salary",
  "amount": 25000,
  "category": "Salary",
  "transaction_type": "Income",
  "transaction_date": "2026-11-05"
}
```

### API Response

A successful creation returns HTTP status `201` with the created transaction as JSON.

Invalid data returns HTTP status `400`. A transaction that does not exist returns HTTP status `404`.

## Database Model

The application uses SQLite with a `transactions` table.

| Field | Data Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| title | TEXT | Transaction title |
| amount | REAL | Transaction amount |
| category | TEXT | Transaction category |
| transaction_type | TEXT | Income or Expense |
| transaction_date | TEXT | Transaction date in YYYY-MM-DD format |

The database is initialized automatically. Transaction records remain stored across application restarts.

## Financial Calculations

- **Total Income:** Sum of all income transactions.
- **Total Expenses:** Sum of all expense transactions.
- **Net Savings:** Total Income − Total Expenses.

Dashboard figures are calculated directly from the SQLite database.

## Validation

Client-side validation uses HTML form attributes such as `required`, `min`, and `step`.

Server-side validation independently checks transaction titles, positive numeric amounts, valid transaction types, matching categories, and valid dates before database operations.
