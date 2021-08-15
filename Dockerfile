FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app/
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt
