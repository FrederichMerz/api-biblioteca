from fastapi import FastAPI, HTTPException, Depends, Query, Request, Body
from sqlalchemy.orm import Session
from database import sesion, inicializar_bd
from models import Autor, Libro
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import re



load_dotenv()
inicializar_bd()


app = FastAPI(title="API Biblioteca", version="1.0")


def get_db():
    db = sesion()
    try:
        yield db
    finally:
        db.close()

# crear autor
@app.post("/api/autores", status_code=201)
def crear_autor(
    nombre: str = Body(..., description="Nombre del autor"),
    nacionalidad: str = Body(None, description="Nacionalidad del autor"),
    fecha_nacimiento: str = Body(None, description="Fecha de nacimiento en formato YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    if not nombre or not nombre.strip():
        raise HTTPException(status_code=400, detail="El campo nombre es requerido y debe contener al menos una letra.")

    fecha_obj = None
    if fecha_nacimiento:
        try:
            fecha_obj = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="La fecha debe tener el formato YYYY-MM-DD")
        
    nuevo_autor = Autor(
        nombre=nombre,
        nacionalidad=nacionalidad,
        fecha_nacimiento=fecha_obj
    )
    db.add(nuevo_autor)
    db.commit()
    db.refresh(nuevo_autor)

    return {
        "id": nuevo_autor.id,
        "nombre": nuevo_autor.nombre,
        "nacionalidad": nuevo_autor.nacionalidad,
        "fecha_nacimiento": str(nuevo_autor.fecha_nacimiento) if nuevo_autor.fecha_nacimiento else None
    }

# listar autores
@app.get("/api/autores")
def listar_autores(
    pagina: int = Query(1, ge=1, description="Numero de pagina desde 1"),
    tamano: int = Query(10, ge=1, le=100, description="Cantidad de resultados por pagina"),
    db: Session = Depends(get_db)
):

    skip = (pagina - 1) * tamano

    total = db.query(Autor).count()
    autores = db.query(Autor).offset(skip).limit(tamano).all()

    total_pages = (total + tamano - 1) // tamano 

    
    return {
        "pagina": pagina,
        "tamano": tamano,
        "total_items": total,
        "total_pages": total_pages,
        "autores": autores
    }

# consultar autor por id
@app.get("/api/autores/{autor_id}")
def obtener_autor(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor


#actualizar autor
@app.put("/api/autores/{autor_id}")
def actualizar_autor(
    autor_id: int,
    nombre: Optional[str] = Body(None),
    nacionalidad: Optional[str] = Body(None),
    fecha_nacimiento: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):

    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    if nombre is not None:
        if not nombre.strip():
            raise HTTPException(status_code=400, detail="El nombre no puede contener solo espacios.")
        autor.nombre = nombre.strip()
    if nacionalidad is not None:
        if not nacionalidad.strip():
            raise HTTPException(status_code=400,detail="La nacionalidad no puede contener solo espacios.")
        autor.nacionalidad = nacionalidad.strip()
    if fecha_nacimiento:
        try:
            autor.fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="La fecha debe tener formato YYYY-MM-DD")

    db.commit()
    db.refresh(autor)

    return {
        "id": autor.id,
        "nombre": autor.nombre,
        "nacionalidad": autor.nacionalidad,
        "fecha_nacimiento": str(autor.fecha_nacimiento) if autor.fecha_nacimiento else None
    }

# eliminar autor
@app.delete("/api/autores/{autor_id}")
def eliminar_autor(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")

    if autor.libros:
        raise HTTPException(status_code=400, detail="No se puede eliminar un autor con libros asociados")

    db.delete(autor)
    db.commit()
    return {"mensaje": "Autor eliminado correctamente"}

# crear libro
@app.post("/api/libros", status_code=201)
def crear_libro(
    titulo: str = Body(...),
    isbn: str = Body(...),
    autor_id: int = Body(...),
    anio_publicacion: Optional[int] = Body(None, alias="anio_publicacion"),
    genero: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    
    if not titulo or not titulo.strip() or not re.search(r"[A-Za-z]", titulo):
        raise HTTPException(status_code=400, detail="El titulo es requerido y debe contener al menos una letra.")
    
    if not isbn or not re.match(r"^(?:\d[-]?){9,12}\d$", isbn):
        raise HTTPException(status_code=400, detail="El ISBN debe tener entre 10 y 13 digitos numericos y puede incluir guiones (-)")

    autor = db.query(Autor).filter(Autor.id == autor_id).first()
    if not autor:
        raise HTTPException(status_code=400, detail="El autor no existe")

    if db.query(Libro).filter(Libro.isbn == isbn).first():
        raise HTTPException(status_code=400, detail="El ISBN ya existe")
    
    if not isinstance(anio_publicacion, int):
        raise HTTPException(status_code=400, detail="El año de publicacion debe ser un numero entero.")
    
    if anio_publicacion <= 0:
        raise HTTPException(status_code=400, detail="El año de publicacion no puede ser 0 ni negativo.")
    
    if genero is not None:
        if not genero.strip():
            raise HTTPException(
                status_code=400,
                detail="El campo genero no debe contener solo espacios."
            )
        genero = genero.strip()

    nuevo_libro = Libro(
        titulo=titulo,
        isbn=isbn,
        autor_id=autor_id,
        año_publicacion=anio_publicacion,
        genero=genero,
        disponible=True  
    )

    db.add(nuevo_libro)
    db.commit()
    db.refresh(nuevo_libro)

    return {
        "id": nuevo_libro.id,
        "titulo": nuevo_libro.titulo,
        "isbn": nuevo_libro.isbn,
        "autor_id": nuevo_libro.autor_id,
        "autor": {
            "id": autor.id,
            "nombre": autor.nombre
        },
        "año_publicacion": nuevo_libro.año_publicacion,
        "genero": nuevo_libro.genero,
        "disponible": nuevo_libro.disponible
    }

# listar libros
@app.get("/api/libros")
def listar_libros(
    disponible: Optional[bool] = Query(None, description="Filtrar libros disponibles o no"),
    pagina: int = Query(1, ge=1, description="Numero de pagina desde 1"),
    tamano: int = Query(10, ge=1, le=100, description="Cantidad de resultados por pagina"),
    db: Session = Depends(get_db)
):
    query = db.query(Libro)
    if disponible is not None:
        query = query.filter(Libro.disponible == disponible)

   
    total_items = query.count()

    offset = (pagina - 1) * tamano

    libros = query.offset(offset).limit(tamano).all()

    total_paginas = (total_items + tamano - 1) // tamano  

    resultado = []
    for libro in libros:
        resultado.append({
            "id": libro.id,
            "titulo": libro.titulo,
            "isbn": libro.isbn,
            "autor_id": libro.autor_id,
            "autor": {
                "id": libro.autor_id,
                "nombre": libro.autor.nombre if libro.autor else None,
                "nacionalidad": libro.autor.nacionalidad if libro.autor else None,
                "fecha_nacimiento": str(libro.autor.fecha_nacimiento) if libro.autor and libro.autor.fecha_nacimiento else None
            },
            "año_publicacion": libro.año_publicacion,
            "genero": libro.genero,
            "disponible": libro.disponible
        })

    return {
        "pagina": pagina,
        "tamano": tamano,
        "total_items": total_items,
        "total_paginas": total_paginas,
        "libros": resultado
    }

# buscar libros por titulo (/api/libros/buscar?={texto})
@app.get("/api/libros/buscar")
def buscar_libros(
    titulo: str = Query(..., description="Texto del titulo a buscar"),
    pagina: int = Query(1, ge=1, description="Numero de pagina desde 1"),
    tamano: int = Query(10, ge=1, le=100, description="Cantidad de resultados por pagina"),
    db: Session = Depends(get_db)
):
    query = db.query(Libro).filter(Libro.titulo.ilike(f"%{titulo}%"))

    total = query.count()

    if total == 0:
        raise HTTPException(status_code=404, detail="No se encontraron libros con ese título")

    
    skip = (pagina - 1) * tamano

    resultados = query.offset(skip).limit(tamano).all()

    total_paginas = (total + tamano - 1) // tamano

    libros_data = [
        {
            "id": libro.id,
            "titulo": libro.titulo,
            "isbn": libro.isbn,
            "autor_id": libro.autor_id,
            "autor": {
                "id": libro.autor.id,
                "nombre": libro.autor.nombre
            } if libro.autor else None,
            "año_publicacion": libro.año_publicacion,
            "genero": libro.genero,
            "disponible": libro.disponible
        }
        for libro in resultados
    ]

    return {
        "pagina": pagina,
        "tamano": tamano,
        "total_resultados": total,
        "total_paginas": total_paginas,
        "libros": libros_data
    }

# consultar libro por id
@app.get("/api/libros/{libro_id}")
def obtener_libro(libro_id: int, db: Session = Depends(get_db)):
    libro = db.query(Libro).filter(Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    

    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "isbn": libro.isbn,
        "autor_id": libro.autor_id,
        "autor": {
            "id": libro.autor_id,
            "nombre": libro.autor.nombre if libro.autor else None,        
        },
        "año_publicacion": libro.año_publicacion,
        "genero": libro.genero,
        "disponible": libro.disponible
    }

# actualizar libro
@app.put("/api/libros/{libro_id}")
def actualizar_libro(
    libro_id: int,
    body: dict = Body(..., example={
        "titulo": "Nuevo titulo",
        "isbn": "123-4567890123",
        "autor_id": 1,
        "año_publicacion": 2025,
        "genero": "Ficción",
        "disponible": True
    }),
    db: Session = Depends(get_db)
):
    libro = db.query(Libro).filter(Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    titulo = body.get("titulo")
    isbn = body.get("isbn")
    autor_id = body.get("autor_id")
    año_publicacion = body.get("año_publicacion")
    genero = body.get("genero")
    disponible = body.get("disponible")

    

    if autor_id:
        autor = db.query(Autor).filter(Autor.id == autor_id).first()
        if not autor:
            raise HTTPException(status_code=400, detail="El autor especificado no existe")
        libro.autor_id = autor_id

    if isbn:
        if not re.fullmatch(r"^(?:\d[-]?){9,12}\d$", isbn):
            raise HTTPException(status_code=400, detail="El ISBN debe tener entre 10 y 13 digitos numericos y puede incluir guiones (-).")

        otro_libro = db.query(Libro).filter(Libro.isbn == isbn, Libro.id != libro_id).first()
        if otro_libro:
            raise HTTPException(status_code=400, detail="El ISBN ya existe en otro libro.")

        libro.isbn = isbn

    if año_publicacion is not None:
        if not isinstance(año_publicacion, int):
            raise HTTPException(status_code=400, detail="El año de publicacion debe ser un numero entero.")
        if año_publicacion <= 0:
            raise HTTPException(status_code=400, detail="El año de publicacion no puede ser 0 ni negativo.")
        libro.año_publicacion = año_publicacion

    if genero is not None:
        if not genero.strip():
            raise HTTPException(
                status_code=400,
                detail="El campo genero no debe contener solo espacios."
            )
        genero = genero.strip()

    if disponible is not None:
        libro.disponible = bool(disponible)

    db.commit()
    db.refresh(libro)

    return {
        "id": libro.id,
        "titulo": libro.titulo,
        "isbn": libro.isbn,
        "autor_id": libro.autor_id,
        "autor": {
            "id": libro.autor.id,
            "nombre": libro.autor.nombre,
            "nacionalidad": libro.autor.nacionalidad,
            "fecha_nacimiento": str(libro.autor.fecha_nacimiento) if libro.autor.fecha_nacimiento else None
        } if libro.autor else None,
        "año_publicacion": libro.año_publicacion,
        "genero": libro.genero,
        "disponible": libro.disponible
    }

#eliminar libro
@app.delete("/api/libros/{libro_id}")
def eliminar_libro(libro_id: int, db: Session = Depends(get_db)):
    libro = db.query(Libro).filter(Libro.id == libro_id).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    db.delete(libro)
    db.commit()
    return {"mensaje": "Libro eliminado correctamente"}



host = os.getenv("HOST")
port = int(os.getenv("PORT"))    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=host, port=port, reload=True)

