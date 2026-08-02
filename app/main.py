"""Member portal — application entry point.

Route map:
    GET  /                     list all members (stands in for an admin view)
    GET  /members/{id}         member detail
    GET  /members/{id}/edit    edit form
    POST /members/{id}/edit    apply changes
    GET  /members/{id}/download?format=json|csv
    GET  /health               liveness probe for the deploy phase
"""

import csv
import io
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.db import LANGUAGES, get_all_members, get_member, init_db, update_member


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup, before the app accepts traffic.

    Code after `yield` runs on shutdown — the place for closing connection
    pools or flushing buffers. Replaces the deprecated @app.on_event hooks.
    """
    init_db()
    yield


app = FastAPI(title="Member Portal", lifespan=lifespan)
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/health")
def health():
    """Deployment platforms poll this to decide if the app is alive."""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def list_members(request: Request):
    return templates.TemplateResponse(
        "list.html",
        {"request": request, "members": get_all_members(), "languages": LANGUAGES},
    )


@app.get("/members/{member_id}", response_class=HTMLResponse)
def member_detail(request: Request, member_id: int):
    member = get_member(member_id)
    if not member:
        return HTMLResponse("Member not found", status_code=404)
    return templates.TemplateResponse(
        "detail.html",
        {"request": request, "member": member, "languages": LANGUAGES},
    )


@app.get("/members/{member_id}/edit", response_class=HTMLResponse)
def edit_form(request: Request, member_id: int):
    member = get_member(member_id)
    if not member:
        return HTMLResponse("Member not found", status_code=404)
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "member": member, "languages": LANGUAGES},
    )


@app.post("/members/{member_id}/edit")
def apply_edit(
    member_id: int,
    email: str = Form(...),
    phone: str = Form(""),
    address_line1: str = Form(""),
    city: str = Form(""),
    state: str = Form(""),
    postal_code: str = Form(""),
    language_preference: str = Form("en"),
):
    if not get_member(member_id):
        return HTMLResponse("Member not found", status_code=404)

    update_member(
        member_id,
        {
            "email": email,
            "phone": phone,
            "address_line1": address_line1,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "language_preference": language_preference,
        },
    )
    return RedirectResponse(f"/members/{member_id}", status_code=303)


@app.get("/members/{member_id}/download")
def download(member_id: int, format: str = "json"):
    member = get_member(member_id)
    if not member:
        return Response("Member not found", status_code=404)

    filename = f"member-{member['member_number']}"

    if format == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(member.keys()))
        writer.writeheader()
        writer.writerow(member)
        return Response(
            buffer.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.csv"'
            },
        )

    return Response(
        json.dumps(member, indent=2),