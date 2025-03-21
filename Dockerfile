FROM ubuntu:latest

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y python3 python3-pip

# Убираем "EXTERNALLY-MANAGED"
RUN rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED

# Устанавливаем зависимости Python
RUN pip install --break-system-packages fastapi[all] sqlalchemy uvicorn
RUN pip install passlib[bcrypt] python-jose

# Копируем код приложения
COPY todo.py /opt/todo.py
WORKDIR /opt

# Запускаем сервер
CMD ["python3", "-m", "uvicorn", "todo:app", "--host", "0.0.0.0", "--port", "8080"]

