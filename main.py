import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from matcher import match

BASE = Path(__file__).parent
POINTS = json.loads((BASE / "data" / "points.json").read_text(encoding="utf-8"))
POINTS_BY_ID = {p["id"]: p for p in POINTS}

COOKIE = "visited"

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def read_visited(request: Request) -> set[str]:
    raw = request.cookies.get(COOKIE, "")
    return {pid for pid in raw.split(",") if pid in POINTS_BY_ID}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html", {"points": POINTS, "visited": read_visited(request)}
    )


@app.post("/points/{point_id}/check", response_class=HTMLResponse)
async def check(request: Request, point_id: str, photo: UploadFile = File(...)):
    point = POINTS_BY_ID.get(point_id)
    if point is None:
        raise HTTPException(404)

    result = match(await photo.read(), point_id)

    error = result.error
    if not result.ok and error is None:
        guess = POINTS_BY_ID.get(result.guess)
        error = f"На фото не {point['name']}"
        error += f", а скорее {guess['name']}." if guess and guess is not point else "."
        error += " Попробуй снять объект целиком."

    response = templates.TemplateResponse(
        request, "_mark.html", {"point": point, "done": result.ok, "error": error}
    )
    if result.ok:
        visited = read_visited(request) | {point_id}
        response.set_cookie(COOKIE, ",".join(sorted(visited)), max_age=60 * 60 * 24 * 365)
        response.headers["HX-Trigger"] = json.dumps({"visited": {"id": point_id}})
    return response


@app.post("/reset")
async def reset():
    response = HTMLResponse("")
    response.delete_cookie(COOKIE)
    response.headers["HX-Refresh"] = "true"
    return response
