# Member portal

A small member self-service portal — view your information, update it, download it.
Built as a teaching project to walk the full delivery lifecycle from local
development through deployment.

**All data is synthetic.** The seed script fabricates every record. Nothing here
should ever be pointed at real member data.

---

## Run it locally

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

If `python` isn't found on Windows, try `py` instead.

## Run the tests

```bash
pytest -v
```

---

## What's here

```
app/
  main.py       routes — the HTTP layer, nothing else
  db.py         data access — all SQL lives here
  seed.py       synthetic data generation
  templates/    server-rendered HTML
tests/
  test_api.py   endpoint tests
```

The separation is the point. `main.py` never writes SQL; `db.py` never knows
about HTTP. When you change the database you touch one file. When you change a
URL you touch a different one.

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | List members |
| GET | `/members/{id}` | Member detail |
| GET | `/members/{id}/edit` | Edit form |
| POST | `/members/{id}/edit` | Apply changes |
| GET | `/members/{id}/download?format=json\|csv` | Export record |
| GET | `/health` | Liveness probe |

FastAPI also generates interactive API docs at `/docs` for free — worth opening.

---

## Lifecycle roadmap

- [x] **1. Local application** — you are here
- [ ] **2. Version control** — git init, branching, commit hygiene
- [ ] **3. Testing** — expand coverage, understand what's worth testing
- [ ] **4. Containerization** — Dockerfile, why it exists
- [ ] **5. Continuous integration** — GitHub Actions on every push
- [ ] **6. Deployment** — ship it to a free host
- [ ] **7. Observability** — logging, health checks, what breaks in production

---

## Deliberate omissions

This is a learning scaffold, not a production system. Missing on purpose, and
worth adding later as exercises:

- **Authentication.** Right now anyone can view and edit anyone. In a real
  portal this is the first thing you'd build.
- **Authorization.** A member should only reach their own record.
- **Audit logging.** Regulated environments need a record of who changed what.
- **Input validation beyond the basics.** Real forms need server-side rules.
- **Migrations.** Schema changes are handled by recreating the table.
