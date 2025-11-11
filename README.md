
# Tecnologias utilizadas
Python 3.10+
FastAPI
SQLAlchemy  
Uvicorn 
SQLite 
python-dotenv


#  Requisitos Previos

Python 3.10 o superior
Git
pip

# Instalacion Paso a Paso

# Clonar el repositorio

git clone https://github.com/FrederichMerz/api-biblioteca
cd api-biblioteca

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux o Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configuracion del entorno
Crear archivo .env
Copiar archivo .env.sample y dejarlo en .env

# Ejecutar aplicacion
python app.py

# Utilizacion de la API 
Swagger: http://127.0.0.1:8000/docs
Postman: http://127.0.0.1:8000


# Endpoints

# Autores (/api/autores)
POST /api/autores - Crear autor

GET /api/autores?pagina=1$tamano=5 - Listar autores por paginacion

GET /api/autores/{id} - Consultar autor por id

PUT /api/autores/{id} - Actualizar autor

DELETE /api/autores/{id} - Eliminar autor

# Libros (/api/libros)
POST /api/libros - Crear libro

GET /api/libros?pagina=1&tamano=5 - Listar libros por paginacion

GET /api/libros/buscar?titulo=texto&pagina=1&tamano=5 - Buscar por titulo y paginacion

GET /api/libros/{id} - Consultar libro por ID

PUT /api/libros/{id} - Actualizar libro

DELETE /api/libros/{id} - Eliminar libro

# Base de Datos
La aplicacion usa SQLite como base de datos por defecto.
El archivo biblioteca.db se crea automaticamente la primera vez que se ejecuta app.py



