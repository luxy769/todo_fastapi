from fastapi import FastAPI
from routers import tasks, users
from database import Base, engine

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключаем маршруты
app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Welcome to the ToDo API"}

@app.get("/api/healthcheck")
def healthcheck():
    return {"status": "ok"}
