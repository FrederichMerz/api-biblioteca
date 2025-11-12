from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

url_database = os.getenv("URL_DATABASE")


engine = create_engine(
    url_database, connect_args={"check_same_thread": False}
)

sesion = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def inicializar_bd():
    import models
    Base.metadata.create_all(bind=engine)