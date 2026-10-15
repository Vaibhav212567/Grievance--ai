# GrievanceAI — AI-assisted Workflow & Grievance Management

A responsive web app prototype for submitting, classifying, prioritizing and tracking grievances.

## Features
- Citizen grievance submission form
- Keyword-based triage suggestions for category and priority (replaceable with a real AI model)
- Grievance register with search and status filters
- Workflow status management
- Dashboard metrics and category charts
- Flask REST API + SQLite database for local use; Render blueprint included for deployment

## Run locally
1. Install Python 3.10+.
2. In this folder, run:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```
3. Open http://127.0.0.1:5000

## Deploy online with full account control
1. Create a new GitHub repository under your own account.
2. Upload all files in this folder (keep `static/index.html` in the `static` folder).
3. On Render, choose **New + → Blueprint**, connect your repository, and approve the `render.yaml` configuration.
4. Render will create the web service and PostgreSQL database. Open the generated `onrender.com` URL.
5. Manage source code from GitHub and deployment/environment settings from your Render account.

## Important production notes
- This starter does not yet implement login/role-based authorization. Do not expose the admin status-update endpoints publicly for real government/citizen data until authentication and authorization are added.
- Triage is a transparent keyword heuristic, not a connected LLM. Add a server-side AI provider integration only after setting up a secret API key in the host's environment variables; never put API keys in browser JavaScript.
- Add rate limiting, validation, audit logs, privacy policy, backups and secure authentication before real-world deployment.
- The database is configured for SQLite locally and PostgreSQL via `DATABASE_URL` in deployment.
