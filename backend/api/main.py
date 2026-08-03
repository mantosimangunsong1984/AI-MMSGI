from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.api.admin import router as admin_router

from backend.api.chat import router as chat_router

app = FastAPI(
    title="MAIA"
)

app.include_router(
    chat_router,
    prefix="/api",
    tags=["Chat"]
)


app.include_router(
    admin_router,
    tags=["Admin"]
)

app.mount(
    "/static",
    StaticFiles(directory="frontend/static"),
    name="static"
)

templates = Jinja2Templates(
    directory="frontend/templates"
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )