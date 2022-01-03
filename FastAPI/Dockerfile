FROM tiangolo/uvicorn-gunicorn:python3.9
COPY . /app
RUN pip install --no-cache-dir python-telegram-bot python-dotenv emoji fastapi
WORKDIR /app
EXPOSE 6000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6000", "--workers","4"]
