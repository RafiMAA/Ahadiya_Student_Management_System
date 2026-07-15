# Ahadiya School Management System

A full-stack application built with React (Vite) on the frontend and FastAPI (Python) + Supabase (PostgreSQL) on the backend.

## Project Structure
- `/app`: React Frontend (Vite, Tailwind, TypeScript)
- `/backend`: FastAPI Backend (Python, asyncpg, ReportLab, openpyxl)

---

## 🛠 Backend Setup (FastAPI + Supabase)

### 1. Database Setup (Supabase)
1. Create a project on [Supabase](https://supabase.com).
2. Go to the SQL Editor and run the SQL migration files in this exact order:
   - `backend/sql/001_schema.sql` (Creates tables)
   - `backend/sql/002_rls_policies.sql` (Sets up Row Level Security)
   - `backend/sql/003_seed_data.sql` (Seeds mock data, academic year, teachers, and rules)

### 2. Environment Variables
Navigate to the `backend` directory and create a `.env` file:
```bash
cd backend
cp .env.example .env
```
Edit the `.env` file with your credentials:
```env
# Get this from Supabase: Project Settings -> Database -> Connection string (URI)
SUPABASE_DB_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-ID].supabase.co:5432/postgres

# Generate a random 32+ char string
JWT_SECRET=your-super-secret-key-that-is-at-least-32-chars
PDF_SCHOOL_NAME=Ahadiya School
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Run the Backend Locally
Ensure you have Python 3.11+ installed.
```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`. You can view the interactive API docs at `http://localhost:8000/docs`.

---

## 💻 Frontend Setup (React/Vite)

### 1. Environment Variables
Navigate to the `app` directory and create a `.env` file:
```bash
cd app
cp .env.example .env
```
By default, it will connect to your local backend:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### 2. Run the Frontend Locally
Make sure you have Node.js (v18+) installed.
```bash
cd app

# Install dependencies
npm install

# Start the development server
npm run dev
```
The frontend will be available at `http://localhost:3000` (or `http://localhost:5173` depending on Vite's default if 3000 is taken).

---

## 🔐 Default Admin Login
Once both servers are running, you can log in using the seed data credentials:
- **Username:** `admin`
- **Password:** `Admin@2025`

---

## 🎓 Promotion Rules Setup
Before executing any year-end student promotions, an administrator must define the promotion rules. 
The system does not hardcode gender or medium transition rules.
1. Log in as an Administrator or Principal.
2. Navigate to **Academic Year → Promotion Rules** in the sidebar.
3. Configure which classes map to which target classes for the upcoming academic year.
4. Go to **Promotion Preview** to verify the expected transitions before executing the promotion script.
