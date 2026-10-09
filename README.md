# CampusHire — Campus Placement & Internship Portal

A no-third-party-dependency demonstration of a role-based placement portal. Built with HTML, CSS, vanilla JavaScript and Python's standard library. The API enforces role permissions and job eligibility server-side; application data is persisted in a local SQLite database named `campushire.db`.

## Run locally (Windows)
1. Install Python 3.10+ (no npm required).
2. Extract this project folder.
3. Open PowerShell **inside the extracted folder**.
4. Run: `py server.py` (or `python server.py`).
5. Open http://127.0.0.1:8000 in your browser. Keep the terminal open while using it.
6. To stop the server, press `Ctrl+C` in that PowerShell window.

No npm install, API key, paid service, or internet connection is required.

## Create an account
On the sign-in page, choose **Create an account**. Students can enter registration number, department, CGPA, graduation year and optional resume URL. Recruiters can create an account and then submit a company profile for admin approval. Admin registration is intentionally disabled to prevent privilege escalation.

## Demo accounts
| Role | Email | Password |
|---|---|---|
| Student Applicant | `student@campushire.demo` | `Student@123` |
| Company Recruiter | `recruiter@campushire.demo` | `Recruiter@123` |
| Placement Cell Admin | `admin@campushire.demo` | `Admin@123` |

These are demo credentials only. Do not use real personal information or deploy this demo publicly as a production service.

The seeded student profile (IT, CGPA 8.2) has an eligible **Web Development Intern** opening available to apply to; the Software Development Intern example is already applied to in the seed data.

## Demo walkthrough
1. Sign in as Student. Open **My Profile** to inspect registration number, department, CGPA, graduation year and resume URL. Try applying to an approved job. The server checks minimum CGPA, allowed department, resume presence, duplicate applications, and job/company approval.
2. Sign in as Recruiter. Submit a company profile and/or a job posting. They begin as `pending`. Open **Applicants** to change candidate status.
3. Sign in as Placement Admin. Open **Approvals**, approve/reject companies and job postings. Open **Audit log** to see timestamp, admin ID, action, entity and details.
4. Restart the server and sign in again with the same account. Accounts, jobs and applications remain in `campushire.db`.

## Architecture and limitations
- `server.py`: standard-library HTTP API, in-memory demo sessions, role authorization, server-side eligibility validation and audit records.
- `campushire.db`: local persistent SQLite database, initialized with sample data on first run.
- `index.html`, `style.css`, `script.js`: responsive UI.
- Sessions are in memory and expire when the server restarts. Demo passwords are stored in the local database in plaintext. Newly registered passwords are also stored in plaintext; this is not production-grade authentication. This is suitable only for a local recruitment demo—not production authentication.
- Recruiter demo user manages the seeded demo companies/jobs. New company submissions are pending until approved; jobs are hidden from students unless both the job and its company are approved.
- Batch status updates are implemented by submitting the selected updates sequentially through the server.
- To reset demo data, stop the server and delete `campushire.db`; the next start recreates the database and seed data.
- Server binds to `127.0.0.1` only. Do not expose it to the public internet.

### If the new sample opportunity does not appear
The server seeds `campushire.db` only on its first run. If you are using an older database, stop the server with Ctrl+C, rename `campushire.db` to `campushire-old.db`, then restart `py server.py` to create fresh seed data. This resets demo data; back up any applications you need first.


## Deploy publicly on Render (demo deployment)
1. Push `server.py`, `index.html`, `style.css`, `script.js`, `README.md`, `render.yaml`, and `.gitignore` to GitHub.
2. In Render, choose **New → Blueprint**, connect `sruthikanova246-ux/campushire`, and select the repository.
3. Render reads `render.yaml` and creates the web service. Wait for the deploy to finish, then open the `onrender.com` URL.
4. The service binds to Render's assigned port. No npm install or external Python package is needed.

**Important demo limitations:** the free configuration uses `/tmp/campushire.db`, which is temporary. Registered accounts and activity can be lost when the instance restarts or redeploys. Do not use real personal information. This demo stores passwords without production-grade hashing and is not suitable for real public users or sensitive data. For a real deployment, use password hashing, secure sessions, rate limiting, and a persistent managed database (or a plan with persistent disk) before inviting real users.
