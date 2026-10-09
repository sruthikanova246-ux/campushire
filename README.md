# CampusHire

A role-based campus placement and internship portal for students, recruiters, and placement administrators.

**Live Demo:** https://campushire-j5b1.onrender.com

**Tech Stack:** HTML, CSS, JavaScript, Python, SQLite

## Features
- Role-based authentication and dashboards
- Student eligibility validation and applications
- Recruiter job and application management
- Admin approvals and audit logs

## Architecture

```text
Users
  |
Frontend (HTML, CSS, JavaScript)
  |
Backend (Python HTTP Server)
  |
Business Logic & Role-Based Access
  |
SQLite Database
```

## Run Locally

```bash
git clone https://github.com/sruthikanova246-ux/campushire.git
cd campushire
python server.py
```

Open `http://localhost:8000` in your browser.
