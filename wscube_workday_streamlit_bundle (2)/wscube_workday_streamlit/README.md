# WsCube Workday — Streamlit prototype

This prototype follows the employee HRMS mockups: a dashboard with a left navigation bar, daily clock-in, work mode, schedule, assigned core work areas and calendar entry point; plus an end-of-day report with task blocks, outcomes, daily summary, totals and a report-submit-and-clock-out action.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints, usually `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Put `app.py` and `requirements.txt` in a GitHub repository (include README if useful).
2. In Streamlit Community Cloud, choose **Create app**, select the repository and branch, and enter `app.py` as the main file.
3. Deploy and open the generated URL.

## Employee flow

1. Sign in is represented by the employee name field in the sidebar (default demo name: Akansha Khatri).
2. From Dashboard, choose Office or Work from home and click **Clock In**.
3. Use **Daily Reporting** to add work blocks with start/end, core work area, task/activity and outcome.
4. Enter the daily summary and select **Submit Report & Clock Out**.
5. Submitted reports are displayed read-only to the employee. Attendance, calendar and work-area pages are available through the sidebar.

## Important prototype limits

- This is a design and workflow prototype, not a production HRMS. The employee name selector is not authentication; the demo must not contain real employee data.
- SQLite is local to the running app and is not a durable shared database on Streamlit Community Cloud. Replace it with managed PostgreSQL or another persistent database for team use.
- Add role-based access, manager review, audit-logged corrections, password/SSO authentication, server-side validation, backups, HR policy settings, and privacy controls before production deployment.
- Core work areas and the work schedule are sample values in `app.py` and should be configured for each employee/team.
- UI layout follows the supplied visual concept; Streamlit provides functional navigation and inputs but does not reproduce every pixel of a bespoke frontend.
