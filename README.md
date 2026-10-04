# SalesFlow CRM — Full-Stack CRM Platform

SalesFlow CRM is a full-stack customer relationship management platform for managing
customers, sales opportunities, activities, follow-ups, and sales performance.

The application uses a layered FastAPI backend, MySQL database, and a vanilla
JavaScript frontend.

---

## ✨ Features

### Customer Management
- Create, view, update, and delete customers
- Search by customer name, email, or company
- Filter, sort, and paginate customer records
- Customer 360 view with related deals, activities, and follow-ups

### Sales Pipeline
- Kanban-style opportunity pipeline
- Manage deal stages, values, probabilities, and expected close dates
- Move opportunities between pipeline stages
- Persist pipeline changes to MySQL

### Activity Tracking
- Record calls, emails, meetings, demos, notes, and other interactions
- View customer-specific activity timelines
- Track activities chronologically

### Follow-up Management
- Schedule follow-up tasks
- View today's, upcoming, completed, and all follow-ups
- Mark follow-ups as completed or reopen them

### Dashboard
- Customer and opportunity metrics
- Pipeline value and won revenue
- Win conversion rate
- Pipeline stage breakdown
- Recent activities and upcoming follow-ups

### Authentication & Authorization
- JWT-based authentication
- Bcrypt password hashing
- Role-based access control
- `ADMIN` and `SALES_REP` roles
- Sales representatives access assigned customers and opportunities
- Administrators have system-wide access and user management

---

## 🛠️ Tech Stack

### Backend
- Python 3.12+
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- Alembic
- PyMySQL
- PyJWT
- Bcrypt
- Uvicorn

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript (ES6+)

### Database & Testing
- MySQL 8.0
- Pytest
- HTTPX

---

## 🏗️ Architecture

The backend follows a layered architecture:

```text
Router → Service → Model → Database
salesflow-crm/
├── backend/
│   ├── alembic/          # Database migrations
│   ├── app/
│   │   ├── core/         # Configuration, authentication & RBAC
│   │   ├── database/     # Database connection
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── routers/      # API routes
│   ├── tests/            # Automated tests
│   ├── requirements.txt
│   ├── alembic.ini
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── .gitignore
└── README.md
```
---

## 🔒 Authentication & Roles

SalesFlow CRM uses JWT-based authentication with `HS256` and role-based authorization.

| Feature | ADMIN | SALES_REP |
|:---|:---:|:---:|
| View Dashboard | Yes | Assigned Data |
| Manage Users | Yes | No |
| Manage Customers | All | Assigned |
| Manage Opportunities | All | Assigned |
| Activities & Follow-ups | Yes | Yes |

---

## 🚀 Setup & Usage

### Prerequisites

- Python 3.12+
- MySQL 8.0
- Git
- Modern web browser

### 3. Configure the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create `.env` from `.env.example` and configure:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/salesflow
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development
```


### 4. Install Dependencies & Run Backend

Create a virtual environment:

```bash
python -m venv .venv
```

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
alembic upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend API:

`http://localhost:8000`

### 5. Run the Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 3000
```

Open the application:

`http://localhost:3000`

---

## 📚 API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

The API includes endpoints for:

- Authentication
- User management
- Customer management
- Sales opportunities
- Activities
- Follow-ups
- Dashboard analytics

---

## 🧪 Testing

Run the test suite from the `backend` directory:

```bash
cd backend
pytest -v
```

Tests cover:

- Authentication
- Role-based access control
- Customer CRUD
- Search and filtering
- Pagination
- Opportunities
- Activities
- Follow-ups
- Dashboard calculations

---

## 📄 License

This project is for educational and portfolio purposes.
