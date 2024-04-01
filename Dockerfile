FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install
CMD ["poetry", "run", "flask", "--app", "main", "run", "--host", "0.0.0.0"]
