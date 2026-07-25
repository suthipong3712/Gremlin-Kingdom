from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request,Form
from fastapi.responses import RedirectResponse
from database import get_connection

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )
    
@app.get("/king")
async def king(request: Request):
    return templates.TemplateResponse(
     request=request,
     name="king.html"
    )



@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html"
    )

@app.get("/codex")
async def codex(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="codex.html"
    )
    
@app.get("/characters")
async def characters (request:Request):
    return templates.TemplateResponse(
        request=request,
        name="characters.html"
    )
    
@app.get("/timeline")
async def timeline(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="timeline.html"
    )


@app.get("/world")
async def world(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="world.html"
    )


@app.get("/gallery")
async def gallery(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="gallery.html"
    )
    
@app.get("/admin")
async def admin(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html"
    )
    
@app.post("/add-character")
async def add_character(
    name: str = Form(...),
    title: str = Form(""),
    race: str = Form(""),
    age: int = Form(0),
    description: str = Form(""),
    image: str = Form("")
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO characters

    (name,title,race,age,description,image)

    VALUES

    (?,?,?,?,?,?)

    """,(name,title,race,age,description,image))

    conn.commit()

    conn.close()

    return RedirectResponse(
        "/characters",
        status_code=303
    )