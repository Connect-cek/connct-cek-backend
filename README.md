# Connect CEK Backend

## Introduction
This is the backend for **Connect-CEK**, an alumni-student interaction platform designed to facilitate communication, mentoring, and networking. This service is built using **FastAPI** and includes support for **user authentication**, **messaging**, **resume processing**, and **file management**.

## Features
- **User authentication** using OTP-based email verification
- **Role-based access control** for students, alumni, mentors, and admins
- **Messaging system** for alumni-student interactions
- **Resume Upload & Parsing** with optional LLM integration
- **User profiles** including resumes and areas of interest
- **Admin panel for user approval and monitoring**
- **Post-based discussion system** for sharing updates

---

## Technologies Used
- [**FastAPI**](https://fastapi.tiangolo.com/) - High-performing web API framework
- [**SQLAlchemy**](https://www.sqlalchemy.org/) - Database ORM for PostgreSQL
- [**PostgreSQL**](https://www.postgresql.org/) - Relational Database
- [**Pydantic**](https://pydantic-docs.helpmanual.io/) - Data validation
- [**JWT Authentication**](https://jwt.io/) - Secure authentication mechanism
- [**Docker & Docker Compose**](https://www.docker.com/) - Containerized deployment
- [**Uvicorn**](https://www.uvicorn.org/) - ASGI server for FastAPI

---

## Project Structure 
```
connect-cek-backend/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── scripts/
│   └── wait-for-it.sh
├── uploads/                    # Directory for storing user-uploaded files
├── app/
│   ├── main.py                  # Entry point of the application
│   ├── config.py                 # App configuration settings
│   ├── database.py               # Database connection setup
│   ├── routers/                  # API route handlers
│   ├── models/                   # Database models (Users, Messages, Posts, etc.)
│   ├── schemas/                  # Pydantic schemas for request/response validation
│   ├── services/                 # Business logic for emails, resume processing, OTPs, etc.
│   ├── utils/                    # Utility functions (authentication, validation, etc.)
│   ├── __init__.py
```
---

## Installation & Setup

### 1. Prerequisites
Ensure you have the following installed:
- Python 3.10+
- PostgreSQL 14 or later
- Docker & Docker Compose (if using containers)

---

### 2. Clone the Repository
```bash
git clone https://github.com/your-org/connect-cek-backend.git
cd connect-cek-backend
```

---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Set Up Environment Variables
Create a **`.env`** file in the project root and define required configurations:
```ini
ADMIN_EMAIL=admin@example.com
DATABASE_URL=postgresql://user:password@db/connect_db
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-email-password
COLLEGE_ID=CEK
OTP_EXPIRY_MINUTES=10
TOKEN_SECRET_KEY=your-secret-key
TOKEN_EXPIRE_MINUTES=60
LLM_API_KEY=your-llm-api-key (optional)
LLM_API_ENDPOINT=your-llm-api-endpoint (optional)
```

---

### 5. Database Setup
Ensure that the `.env` file is correctly configured with your PostgreSQL credentials.

To create the tables, run:

```bash
python -m app.database
```

Alternatively, if you're using **Docker Compose**, the database is automatically initialized.

---

### 6. Running the Application

#### **Option A: Running Locally**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### **Option B: Running with Docker**
Build and start the containers:
```bash
docker-compose up --build
```

Once running, access the API here:
- **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## API Endpoints

| Endpoint                        | HTTP Method | Description |
|----------------------------------|------------|-------------|
| `/auth/send-otp`                | `POST`     | Sends an OTP for email verification |
| `/auth/verify-otp`              | `POST`     | Verifies the OTP and logs in users |
| `/users/register`               | `POST`     | Registers a new user with profile |
| `/users/profile`                | `GET`      | Fetches user profile |
| `/users/profile`                | `PUT`      | Updates user profile |
| `/messages/`                    | `POST`     | Sends a message to another user |
| `/messages/conversations`       | `GET`      | Fetches a user's conversations |
| `/resume/upload`                | `POST`     | Uploads & processes a resume |
| `/admin/pending-registrations`  | `GET`      | Fetches pending user registrations |
| `/admin/approve-user/{user_id}` | `PUT`      | Approves a pending user |
| `/admin/user/{user_id}`         | `DELETE`   | Deletes a user |
| `/admin/message`                | `POST`     | Sends admin message to a user |

For the complete API documentation, visit [Swagger UI](http://localhost:8000/docs).

---

## Deployment

### **Deploying to a Cloud Server (Docker)**
If deploying to a cloud server:
1. Modify `.env` file with production settings
2. Run:
   ```bash
   docker-compose up --build -d
   ```