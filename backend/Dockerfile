FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 👇 Copy only the 'app' folder inside backend into /app
COPY ./app ./app

EXPOSE 8000

# 👇 Since the app is inside /app/app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
