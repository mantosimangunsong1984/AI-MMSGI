from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

print("ADMIN ROUTER LOADED")

router = APIRouter()

templates = Jinja2Templates(
    directory="frontend/templates"
)


@router.get(
    "/admin",
    response_class=HTMLResponse
)
async def admin_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin.html"
    )
