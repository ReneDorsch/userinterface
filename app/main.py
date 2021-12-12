import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from static.routers import advanced, analysis, enrichment, edit
from app.internal.tasks import document_enrichment, document_annotation

app = FastAPI()
templates = Jinja2Templates(directory="static/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(advanced.router)
app.include_router(analysis.router)
app.include_router(enrichment.router)
app.include_router(edit.router)
app.include_router(document_enrichment.router)
app.include_router(document_annotation.router)


@app.get("/", response_class=HTMLResponse)
def hello_world(request: Request):
    id = 0
    return templates.TemplateResponse("start.html", {"request": request, "id": id, "title": "Item", "active": False})


@app.get("/about", response_class=HTMLResponse)
def hello_world(request: Request):
    id = 0
    return templates.TemplateResponse("about.html", {"request": request, "id": id, "title": "Item", "active": True})


@app.get("/item/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id, "title": "Item", "active": True})



if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)




