FROM python:3.11-slim

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
EXPOSE 5000

RUN mkdir -p /app/preprocessor/key
# Copy the JSON secret into the expected path inside the container
COPY preprocessor/key/predictivemaintenancesystem-firebase-adminsdk-w2tny-15b2aec14c.json /app/preprocessor/key/predictivemaintenancesystem-firebase-adminsdk-w2tny-15b2aec14c.json

# CMD ["python", "-m", "preprocessor.main"]

# Change this line - run main.py directly from the preprocessor directory
CMD ["python", "main.py"]