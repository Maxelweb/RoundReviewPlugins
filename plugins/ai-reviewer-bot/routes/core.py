import base64
import io
import os
import threading

import requests
from flask import Blueprint, render_template, request, redirect, session, url_for
from pypdf import PdfReader

from config import (
    API_BASE_URL,
    API_KEY,
    DASHBOARD_PASSWORD,
    LLM_API_KEY,
    LLM_API_TYPE,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_TIMEOUT_SECONDS,
    PLUGIN_NAME,
    PLUGIN_VERSION,
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_FILE,
    log,
)


core_blueprint = Blueprint("core", __name__, template_folder="../templates")
review_jobs = set()
review_jobs_lock = threading.Lock()


def _headers() -> dict:
    headers = {"x-api-key": API_KEY}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    return headers


def _api_headers() -> dict:
    return {"x-api-key": API_KEY}


def _api_type() -> str:
    if LLM_API_TYPE in {"ollama", "openai"}:
        return LLM_API_TYPE
    return "ollama" if LLM_BASE_URL.endswith(":11434") else "openai"


def llm_health() -> tuple[bool, str]:
    try:
        if _api_type() == "ollama":
            response = requests.get(f"{LLM_BASE_URL}/api/tags", timeout=10)
        else:
            response = requests.get(f"{LLM_BASE_URL}/models", headers=_headers(), timeout=10)
        if response.ok:
            return True, "connected"
        return False, f"HTTP {response.status_code}"
    except requests.RequestException as error:
        return False, str(error)


def get_system_prompt() -> str:
    try:
        with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as prompt_file:
            return prompt_file.read()
    except FileNotFoundError:
        return SYSTEM_PROMPT


def save_system_prompt(prompt: str) -> None:
    parent = os.path.dirname(SYSTEM_PROMPT_FILE)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(SYSTEM_PROMPT_FILE, "w", encoding="utf-8") as prompt_file:
        prompt_file.write(prompt)


def _extract_text(raw_pdf: str) -> str:
    pdf_data = base64.b64decode(raw_pdf)
    reader = PdfReader(io.BytesIO(pdf_data))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()


def _call_llm(document_text: str) -> str:
    prompt = get_system_prompt()
    if _api_type() == "ollama":
        payload = {
            "model": LLM_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": document_text},
            ],
        }
        response = requests.post(
            f"{LLM_BASE_URL}/api/chat", json=payload, timeout=LLM_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": document_text},
        ],
        "stream": False,
    }
    response = requests.post(
        f"{LLM_BASE_URL}/chat/completions",
        headers={**_headers(), "Content-Type": "application/json"},
        json=payload,
        timeout=LLM_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _update_review(review_id: str, value: str) -> None:
    response = requests.put(
        f"{API_BASE_URL}/integrations/reviews/{review_id}",
        headers={**_api_headers(), "Content-Type": "application/json"},
        json={"value": value},
        timeout=30,
    )
    response.raise_for_status()


def _review_document(object_id: str, review_id: str) -> None:
    try:
        response = requests.get(
            f"{API_BASE_URL}/objects/{object_id}?raw=1",
            headers=_api_headers(),
            timeout=30,
        )
        response.raise_for_status()
        raw_pdf = response.json()["object"]["raw"]
        document_text = _extract_text(raw_pdf)
        result = _call_llm(document_text)
        _update_review(review_id, result)
        log.info("AI review completed for object %s", object_id)
    except Exception as error:
        log.exception("AI review failed for object %s: %s", object_id, error)
        try:
            _update_review(review_id, f"AI review failed: {error}")
        except requests.RequestException:
            log.exception("Unable to publish AI review failure for object %s", object_id)
    finally:
        with review_jobs_lock:
            review_jobs.discard(object_id)


def _create_review(project_id: str, object_id: str) -> str | None:
    response = requests.post(
        f"{API_BASE_URL}/projects/{project_id}/objects/{object_id}/integrations/reviews",
        headers={**_api_headers(), "Content-Type": "application/json"},
        json={
            "name": PLUGIN_NAME,
            "value": "Bot is starting reviewing the document. Updates will be published here",
            "icon": "robot",
        },
        timeout=30,
    )
    if response.status_code == 201:
        return response.json()["review_id"]
    if response.status_code == 409:
        reviews = requests.get(
            f"{API_BASE_URL}/projects/{project_id}/objects/{object_id}/integrations/reviews",
            headers=_api_headers(),
            timeout=30,
        )
        reviews.raise_for_status()
        for review in reviews.json().get("reviews", []):
            if review.get("name") == PLUGIN_NAME:
                return review["id"]
    response.raise_for_status()
    return None


@core_blueprint.get("/")
def index():
    connected, detail = llm_health()
    return {
        "message": f"Bot {PLUGIN_NAME} (v{PLUGIN_VERSION}) is active",
        "llm_connected": connected,
        "llm_status": detail,
    }, 200


@core_blueprint.post("/webhook")
def handle_webhook():
    data = request.get_json(silent=True)
    if not data or data.get("event") != "object.updated":
        return {"error": "Invalid payload"}, 400
    if data.get("updated_fields", {}).get("status") != "Pending Review":
        return {"message": "Notification ignored"}, 200

    object_id = data.get("object_id")
    project_id = data.get("project_id")
    with review_jobs_lock:
        if object_id in review_jobs:
            return {"message": "Review already in progress"}, 200
        review_jobs.add(object_id)
    try:
        review_id = _create_review(project_id, object_id)
        if not review_id:
            raise RuntimeError("Unable to create integration review")
        threading.Thread(
            target=_review_document,
            args=(object_id, review_id),
            daemon=True,
        ).start()
        return {"message": "Review started"}, 202
    except Exception as error:
        with review_jobs_lock:
            review_jobs.discard(object_id)
        log.exception("Unable to start review for object %s: %s", object_id, error)
        return {"error": "Unable to start review"}, 500


@core_blueprint.post("/dashboard/logout")
def dashboard_logout():
    session.pop("dashboard_authenticated", None)
    return redirect(url_for("core.dashboard"))


@core_blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not DASHBOARD_PASSWORD:
        return "DASHBOARD_PASSWORD is not configured", 503
    template_context = {"plugin_info": (PLUGIN_NAME, PLUGIN_VERSION)}
    if request.method == "POST":
        if request.form.get("password", "") == DASHBOARD_PASSWORD:
            session["dashboard_authenticated"] = True
            return redirect(url_for("core.dashboard"))
        else:
            return render_template(
                "dashboard.html", **template_context, error="Invalid password"
            ), 401
    if not session.get("dashboard_authenticated"):
        return render_template("dashboard.html", **template_context, login=True)

    connected, detail = llm_health()
    if not connected:
        return render_template(
            "dashboard.html", **template_context, unavailable=detail
        ), 503
    if request.method == "POST":
        save_system_prompt(request.form.get("system_prompt", ""))
        return redirect(url_for("core.dashboard"))
    return render_template(
        "dashboard.html",
        **template_context,
        connected=True,
        ai_model=LLM_MODEL,
        ai_type=_api_type(),
        ai_url=LLM_BASE_URL,
        system_prompt=get_system_prompt(),
    )