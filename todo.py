from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Константы для аутентификации
SECRET_KEY = "your_secret_key"  # Замените на ваш собственный секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# База данных SQLite
DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Создаем приложение FastAPI
app = FastAPI()

# Модели данных для задач и пользователей
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Создание базы данных
Base.metadata.create_all(bind=engine)

# Настройка безопасности
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Функции для работы с пользователями и паролями
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Зависимости
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Модели для работы с пользователями и аутентификацией
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Регистрация нового пользователя
@app.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    # Проверка, существует ли уже пользователь с таким именем
    db_user = get_user(db, username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Хеширование пароля и создание нового пользователя
    hashed_password = get_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

# Окончание реализации аутентификации
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Получение задач, доступных для аутентифицированного пользователя
@app.post("/tasks/")
def create_task(title: str, description: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_info = verify_token(token)
    if user_info is None:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    task = Task(title=title, description=description)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks/")
def read_tasks(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_info = verify_token(token)
    if user_info is None:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return db.query(Task).all()

@app.get("/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_info = verify_token(token)
    if user_info is None:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user_info = verify_token(token)
    if user_info is None:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
