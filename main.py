from fastapi import FastAPI, Request, Form, UploadFile, File

from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import get_connection

import os
import shutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/king")
async def king(request: Request):
    return templates.TemplateResponse(request=request, name="king.html")


@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse(request=request, name="history.html")


@app.get("/codex")
async def codex(request: Request):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
            SELECT *
            FROM characters
            ORDER BY id
    """)
    characters = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse(
        request=request, name="codex.html", context={"characters": characters}
    )


@app.get("/characters")
async def characters(request: Request):
    return templates.TemplateResponse(request=request, name="characters.html")


@app.get("/timeline")
async def timeline(request: Request):
    return templates.TemplateResponse(request=request, name="timeline.html")


@app.get("/world")
async def world(request: Request):
    return templates.TemplateResponse(request=request, name="world.html")


@app.get("/gallery")
async def gallery(request: Request):
    return templates.TemplateResponse(request=request, name="gallery.html")


@app.get("/admin")
async def admin(request: Request):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM characters
        ORDER BY id DESC
    """)

    characters = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        request=request, name="admin.html", context={"characters": characters}
    )


@app.get("/edit-character/{character_id}")
async def edit_character(request: Request, character_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT *
        FROM characters
        WHERE id = ?
        """,
        (character_id,),
    )
    character = cursor.fetchone()
    conn.close()
    return templates.TemplateResponse(
        request=request, name="edit_character.html", context={"character": character}
    )


@app.post("/update-character/{character_id}")
async def update_character(
    character_id: int,
    name: str = Form(...),
    title: str = Form(""),
    race: str = Form(""),
    age: int = Form(0),
    home: str = Form(""),
    relationship: str = Form(""),
    description: str = Form(""),
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE characters
        SET
            name = ?,
            title = ?,
            race = ?,
            age = ?,
            home = ?,
            relationship = ?,
            description = ?
        WHERE id = ?
    """,
        (name, title, race, age, home, relationship, description, character_id),
    )

    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/character/{character_id}", status_code=303)


@app.post("/add-character")
async def add_character(
    name: str = Form(...),
    title: str = Form(""),
    race: str = Form(""),
    age: int = Form(0),
    home: str = Form(""),
    relationship: str = Form(""),
    description: str = Form(""),
    image: UploadFile = File(...),
):
    filename = image.filename
    filepath = os.path.join("static", "images", "characters", filename)
    os.makedirs("static/images/characters", exist_ok=True)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """

    INSERT INTO characters

    (name,title,race,age,home,relationship,description,image)

    VALUES

    (?,?,?,?,?,?,?,?)

    """,
        (
            name,
            title,
            race,
            age,
            home,
            relationship,
            description,
            f"/static/images/characters/{filename}",
        ),
    )

    conn.commit()

    conn.close()

    return RedirectResponse("/codex", status_code=303)


@app.get("/character/{character_id}")
async def character_detail(request: Request, character_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
            SELECT *
            FROM characters
            WHERE id = ?
            """,
        (character_id,),
    )
    character = cursor.fetchone()
    conn.close()
    return templates.TemplateResponse(
        request=request, name="character.html", context={"character": character}
    )


@app.get("/delete-character/{character_id}")
async def delete_character(character_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM characters WHERE id=?", (character_id,))

    conn.commit()
    conn.close()

    return RedirectResponse(url="/admin", status_code=303)
