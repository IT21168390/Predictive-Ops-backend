# FROM python:3.12.4
# WORKDIR /pdm
# COPY . .
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt
# EXPOSE 8000
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "run:preprocessor/main.py" ]

FROM python:3.12.10-slim

# ---- system ---------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# ---- python ---------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- code -----------------------------------------------------------------
COPY . .

# FastAPI listens on :8000
EXPOSE 8000

CMD ["python", "-m", "preprocessor.main"]
