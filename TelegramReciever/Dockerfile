FROM python:3.9
COPY . /app
RUN pip install python-telegram-bot python-dotenv emoji
WORKDIR /app
ENTRYPOINT [ "python", "main.py" ]