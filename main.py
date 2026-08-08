from fastapi import FastAPI, Request, Form, UploadFile, File

from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import get_connection

import os
import shutil
import math

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
async def codex(request: Request, q: str = "", page: int = 1):

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------
    # จำนวนตัวละครต่อ 1 หน้า
    # ----------------------------
    per_page = 8

    if page < 1:
        page = 1

    offset = (page - 1) * per_page

    # ===================================================
    # มีการค้นหา
    # ===================================================
    if q:

        keyword = f"%{q}%"

        # นับจำนวนข้อมูลทั้งหมด
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM characters
            WHERE
                name LIKE ?
                OR title LIKE ?
                OR race LIKE ?
                OR home LIKE ?
                OR relationship LIKE ?
                OR description LIKE ?
        """,
            (keyword, keyword, keyword, keyword, keyword, keyword),
        )

        total_characters = cursor.fetchone()[0]

        # ดึงข้อมูลเฉพาะหน้าที่ต้องการ
        cursor.execute(
            """
            SELECT *
            FROM characters
            WHERE
                name LIKE ?
                OR title LIKE ?
                OR race LIKE ?
                OR home LIKE ?
                OR relationship LIKE ?
                OR description LIKE ?
            ORDER BY id
            LIMIT ?
            OFFSET ?
        """,
            (keyword, keyword, keyword, keyword, keyword, keyword, per_page, offset),
        )

    # ===================================================
    # ไม่มีการค้นหา
    # ===================================================
    else:

        # นับจำนวนตัวละครทั้งหมด
        cursor.execute("""
            SELECT COUNT(*)
            FROM characters
        """)

        total_characters = cursor.fetchone()[0]

        # ดึงข้อมูลเฉพาะหน้าปัจจุบัน
        cursor.execute(
            """
            SELECT *
            FROM characters
            ORDER BY id
            LIMIT ?
            OFFSET ?
        """,
            (per_page, offset),
        )

    characters = cursor.fetchall()

    conn.close()

    # คำนวณจำนวนหน้า
    total_pages = math.ceil(total_characters / per_page)

    return templates.TemplateResponse(
        request=request,
        name="codex.html",
        context={
            "characters": characters,
            "query": q,
            "page": page,
            "total_pages": total_pages,
        },
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
    image: UploadFile | None = File(None),
):

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------------------
    # ดึงข้อมูลตัวละครเดิม
    # -----------------------------------------

    cursor.execute(
        """
        SELECT image
        FROM characters
        WHERE id = ?
        """,
        (character_id,),
    )

    character = cursor.fetchone()

    if character is None:
        conn.close()

        return RedirectResponse(url="/admin", status_code=303)

    old_image = character[0]
    print("OLD IMAGE:", old_image)
    print("IMAGE:", image.filename if image else "NO IMAGE")

    # -----------------------------------------
    # เตรียมรูปภาพ
    # -----------------------------------------

    image_path = old_image

    # ถ้ามีการเลือกรูปใหม่
    if image and image.filename:

        os.makedirs("static/images/characters", exist_ok=True)

        filename = image.filename

        filepath = os.path.join("static", "images", "characters", filename)

        # บันทึกรูปใหม่
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_path = f"/static/images/characters/{filename}"

    # -----------------------------------------
    # UPDATE Database
    # -----------------------------------------

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
            description = ?,
            image = ?
        WHERE id = ?
        """,
        (
            name,
            title,
            race,
            age,
            home,
            relationship,
            description,
            image_path,
            character_id,
        ),
    )

    conn.commit()
    conn.close()

    # -----------------------------------------
    # กลับไปหน้า Character
    # -----------------------------------------

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
