# Placement Portal Application — V2

A campus recruitment portal for an institute's placement cell. It replaces the
spreadsheets-and-email workflow with one system that three roles share:

- **Admin** — the pre-existing superuser. Approves or rejects company
  registrations and placement drives, searches the student and company
  registers, blacklists accounts, and reads placement statistics.
- **Company** — registers, waits for approval, then posts drives, reviews
  applicants, shortlists, schedules interviews and issues offer letters.
- **Student** — self-registers, keeps a profile and resume, browses drives they
  are eligible for, applies, tracks status and accepts or declines offers.

Built for Modern Application Development II.

---

## Features

**Admin** — the only account that cannot self-register; created by `seed.py`.

- Dashboard counting students, companies, drives, applications and placements
- Approve or reject company registrations, and placement drives separately
- Blacklist or restore any company or student
- Search the company register by name, industry, location or HR email
- Search the student register by name, roll number, email or phone
- View every application in the portal, and any student's resume
- Analytics: applications and placements over time, application funnel, skills
  in demand, placements by branch, offer outcomes, acceptance and placement rates

**Company** — registers, then waits for approval. A pending company can sign in
and look around but cannot post anything.

- Dashboard with drive counts, applicants, shortlisted, offers and placements,
  plus queues for what needs attention
- Post drives with eligibility criteria, required skills, experience, salary,
  benefits, openings and a deadline
- Review applicants, open their resumes, and see who applied outside the
  criteria the drive states
- Move applications through shortlisted → interview → offer → rejected, with
  feedback shared back to the candidate
- Schedule interviews, issue offer letters as a generated HTML document
- Export every applicant across its drives as CSV
- Analytics: applicant spread across CGPA and branch, offer-to-acceptance rate

**Student** — self-registers and is active immediately.

- Dashboard with open drives, applications, shortlists, interviews and offers
- Browse and search drives by role, company or required skill; filter by whether
  they have applied and by the CGPA a drive asks for
- See exactly why they do not qualify for a drive, rather than the drive
  silently disappearing
- Apply once per drive, withdraw while still under review
- Track status, interview dates and company feedback
- Accept or decline an offer, and download the offer letter
- Upload a resume (PDF), visible only to companies they have applied to
- Browse the recruiter directory of approved companies
- Export their own application history as CSV

**Everyone**

- Public landing dashboard, pre-login, with aggregate stats and no personal data
- ATS-style resume screener matching a resume against a drive's required skills
- In-app notification bell, plus email for reminders and reports
- Installable as a PWA, and usable on a phone
- Server-side paging, search and sorting on every list

---

## Tech stack

| Layer | Used for |
|---|---|
| **Flask** | JSON API — no server-rendered UI |
| **Vue 3 + Vite** | the entire interface, a single-page app |
| **Bootstrap 5** (via bootstrap-vue-next) | the only CSS framework used |
| **Jinja2** | the offer letter and the monthly report — documents, not UI |
| **SQLite** | the database, created from the models by `seed.py` |
| **Redis** | response caching, and the Celery broker and result backend |
| **Celery + Celery Beat** | two scheduled jobs and one user-triggered job |
| **JWT** (Flask-JWT-Extended) | authentication, with the role as a signed claim |

Redis uses three separate databases so that flushing the cache can never drop
queued jobs: `/0` broker, `/1` results, `/2` cache.

---

## API definition

The full API is described in **`api.yaml`** at the repository root — an OpenAPI
3.0 document covering all 32 paths and 39 operations the application serves.

It records, for each endpoint, the authentication required, the query parameters
accepted, the request body, and the response codes with the reason each is
returned. Bearer JWT applies by default; only four endpoints are public — sign
in, the two registrations, and the public statistics used by the landing page.

Several endpoints return a payload shaped by the caller's role, so the schemas
mark which fields reach which role.

To read it rendered, paste the file into [editor.swagger.io](https://editor.swagger.io).

---

## Setup

Python 3.11+, Node 18+, and a running Redis.

### Redis

On macOS, Homebrew installs Redis as a background service, so it is usually
already running — check before starting a second one:

```bash
redis-cli ping          # PONG means it is up, nothing more to do
```

If it is not:

```bash
brew services start redis     # as a service, survives reboots
redis-server                  # or in the foreground, in its own terminal
```

### Backend dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

*On the development machine the environment already exists one level up, so
only the activate line is needed:*

```bash
source /Users/christianofernandes/developer/iitm_ds_may_2026/.mad2env/bin/activate
```

### Frontend dependencies

```bash
cd frontend && npm install
```

`node_modules` is around 185 MB. If it is already present in the submission
folder, copying it across is faster than reinstalling and needs no network:

```bash
cp -R /path/to/submission/frontend/node_modules frontend/
```

---

## Running it

Four processes once Redis is up, in any order.

```bash
# 1. API — http://localhost:5001
cd backend && python seed.py      # first run only: schema + demo data
cd backend && python run.py

# 2. Celery worker — nothing asynchronous happens without this
cd backend && celery -A make_celery worker --loglevel INFO

# 3. Celery beat — schedules the two recurring jobs
cd backend && celery -A make_celery beat --loglevel INFO

# 4. Frontend — http://localhost:5173
cd frontend && npm run dev
```

The worker and beat are separate processes on purpose: beat only *schedules*,
it never executes. With beat running and no worker, jobs pile up in Redis and
nothing happens.

### Seeding

`seed.py` drops and recreates every table, then writes a realistic dataset:
12 companies (one pending, one rejected), 60 students, 36 drives backdated over
six months, and several hundred applications across every status.

```bash
python seed.py                              # no resumes
python seed.py --resume path/to/any.pdf     # same PDF as every student's resume
```

The `--resume` flag exists because the repo carries no PDF; pass any real one
and the company applicant list has something to open.

### Demo accounts

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Company | any handle printed by the seed | `company123` |
| Student | `student1` … `student60` | `student123` |

`student59` is blacklisted and one company is pending approval, so the
moderation flows have a subject without having to create one.

---

## Configuration

Everything has a working default; `.env` is only needed to change one.

| Variable | Default | Notes |
|---|---|---|
| `JWT_SECRET_KEY` | a dev value | set this for anything real |
| `REDIS_HOST` / `REDIS_PORT` | `localhost:6379` | |
| `SMTP_HOST` | *unset* | see below |
| `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | `587` / unset / unset | |
| `MAIL_FROM` | `placement-cell@institute.edu` | |

**Mail with no mail server.** With `SMTP_HOST` unset, the `send_email` task
writes each message to `backend/instance/outbox/` as a `.eml` file instead of
sending it. That is the full MIME the server would have transmitted, so the
scheduled jobs are demonstrable on a laptop with no mail account — and setting
`SMTP_HOST` is the only change needed to send for real.

---

## Background jobs

| Job | When | What |
|---|---|---|
| `reminders.daily_student_reminders` | daily, 09:00 | emails students about an interview tomorrow, or a drive closing within 3 days they have not applied to |
| `reports.monthly_placement_report` | 1st of the month, 07:00 | renders an HTML placement report and emails it to the admin |
| `exports.student_applications_csv` | on request | a student's own application history as CSV |
| `exports.company_applications_csv` | on request | every applicant across a company's drives |

Every message also lands in the in-app notification bell. The two export jobs
return a task id immediately; the browser polls until the worker reports
success, then downloads the file.

To run one without waiting for its schedule:

```python
from app.tasks.reports import monthly_placement_report
monthly_placement_report.delay()
```

---

## Layout

```
api.yaml           the OpenAPI 3.0 definition of every endpoint

backend/
  app/
    models/        SQLAlchemy models — User, Student, Company, Drive,
                   Application, OfferLetter, Placement, Notification, Admin
    routes/        one blueprint per resource
    serializers/   model -> JSON, shaped per viewer role
    policies.py    who may do what, in which states — Flask-free and query-free
    tasks/         Celery jobs
    utils/         pagination, caching, validation, decorators
  seed.py          schema creation + demo data
  run.py           dev server
  make_celery.py   worker and beat entry point

frontend/src/
  views/           one folder per role
  components/      shared table, modal, charts, layout
  composables/     server-side table state, capabilities, export polling
  services/        one module per API area
  router/          nested routes with per-role guards
```

### Two ideas worth knowing before reading the code

**Capabilities, not client-side rules.** Every list response carries a
`capabilities` block saying which actions exist and from which states. The
frontend renders buttons from it and never hard-codes a rule. `policies.py`
builds that block *and* answers the endpoint's permission check, so what the UI
offers and what the API allows cannot drift apart.

**Cache keys are scoped.** `/api/drives` returns a different list to every
student, so a path-keyed cache would serve one student another's results. Keys
are built by hand as `namespace:version:path:role:userId:query`, and a write
bumps the version — orphaning every key in that namespace at once, without
having to enumerate users.
