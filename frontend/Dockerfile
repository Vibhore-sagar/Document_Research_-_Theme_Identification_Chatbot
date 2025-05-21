# frontend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install Streamlit dependencies
RUN apt-get update && apt-get install -y curl

# Copy and install Python deps
COPY ./app.py .
RUN pip install streamlit requests

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
