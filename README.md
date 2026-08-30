# Repair Shop Management App

A full-stack repair shop management application (similar to Shopmonkey) built with **Vue.js**, **Django**, and **PostgreSQL**.

## Features

- **Customers** – Store customer contact and address
- **Vehicles** – Link vehicles to customers (year, make, model, VIN, license plate)
- **Work orders** – Track jobs with status (pending, in progress, waiting parts, ready for pickup, completed, cancelled)
- **Technicians** – Assign technicians to work orders
- **Estimates** – Create estimates with line items (labor/parts)
- **Invoices** – Generate invoices from work orders
- **Service catalog** – Canned labor and parts for estimates
- **JWT authentication** – Secure API with login/logout

## Tech stack

| Layer    | Technology        |
|----------|--------------------|
| Frontend | Vue 3, Vite, Vue Router, Pinia, Axios |
| Backend  | Django 5, Django REST Framework, Simple JWT |
| Database | PostgreSQL        |

## Project structure

```
Shopmonkey clone/
├── backend/          # Django API
│   ├── config/       # Django settings, urls
│   ├── shop/         # Main app (models, views, serializers)
│   ├── manage.py
│   └── requirements.txt
├── frontend/         # Vue 3 app
│   ├── src/
│   │   ├── views/    # Dashboard, Customers, Vehicles, Work Orders, etc.
│   │   ├── components/
│   │   ├── stores/
│   │   └── router/
│   └── package.json
└── README.md
```

## Setup

### 1. PostgreSQL

Create a database and user (or use defaults):

```sql
CREATE DATABASE repair_shop;
-- Use a user with access, e.g. postgres / your password
```

### 2. Backend (Django)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env: set SECRET_KEY and DATABASE_URL (e.g. postgres://user:password@localhost:5432/repair_shop)

python manage.py migrate
python manage.py createsuperuser   # Create a user to log in with
python manage.py runserver
```

API runs at **http://localhost:8000**.  
Admin: **http://localhost:8000/admin/**  
API root: **http://localhost:8000/api/**

### 3. Frontend (Vue)

```bash
cd frontend
npm install
npm run dev
```

App runs at **http://localhost:5173**.

Optional: create `frontend/.env` with `VITE_API_URL=http://localhost:8000` if your API is on a different host.

## Usage

1. Open **http://localhost:5173** and sign in with the superuser account you created.
2. Add **Customers**, then **Vehicles** (linked to a customer).
3. Create **Work orders** for a vehicle and assign a technician (create technicians in Django admin if needed).
4. Use the **Estimates** and **Invoices** sections (and the API) to build estimates and invoices as you extend the app.

## API overview

| Endpoint            | Description        |
|---------------------|--------------------|
| `POST /api/auth/token/` | Obtain JWT (username, password) |
| `POST /api/auth/token/refresh/` | Refresh JWT |
| `GET/POST /api/customers/` | List/create customers |
| `GET/POST /api/vehicles/` | List/create vehicles (?customer_id= for filter) |
| `GET/POST /api/work-orders/` | List/create work orders (?status= filter) |
| `GET/POST /api/estimates/` | List/create estimates (?work_order_id= filter) |
| `GET/POST /api/invoices/` | List/create invoices |
| `GET/POST /api/technicians/` | List technicians |
| `GET/POST /api/service-items/` | List/create labor/parts catalog |

All API requests (except auth) require the header:  
`Authorization: Bearer <access_token>`.

## Next steps

- Add work order create/edit form and estimate builder in the Vue app
- Add invoice creation from estimates and payment tracking
- Add reporting (dashboard stats, revenue, etc.)
- Optional: SMS/email for estimates and invoices, multi-location support
