FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

RUN rm -f /usr/lib/python3.*/EXTERNALLY-MANAGED

RUN pip install --break-system-packages fastapi[all] sqlalchemy uvicorn
RUN pip install passlib[bcrypt] python-jose

COPY todo.py /opt/todo.py
WORKDIR /opt

CMD ["python3", "-m", "uvicorn", "todo:app", "--host", "0.0.0.0", "--port", "8080"]

