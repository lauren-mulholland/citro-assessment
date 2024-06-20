FROM python:3.10.14
COPY requirements.txt ./app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./app ./app
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]