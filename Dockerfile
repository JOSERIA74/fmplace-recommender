FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ✅ Línea clave para incluir el Excel
COPY matriz.xlsx .

CMD ["python", "main.py"]
