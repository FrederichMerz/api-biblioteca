from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Autor(Base):
    __tablename__ = "autor"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    nacionalidad = Column(String, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)

    libros = relationship("Libro", back_populates="autor")


class Libro(Base):
    __tablename__ = "libro"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    autor_id = Column(Integer, ForeignKey("autor.id"), nullable=False)
    año_publicacion = Column(Integer, nullable=True)
    genero = Column(String, nullable=True)
    disponible = Column(Boolean, default=True)

    autor = relationship("Autor", back_populates="libros")
