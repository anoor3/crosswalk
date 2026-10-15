FROM python:3.12-slim

WORKDIR /app
COPY . /app
RUN python -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
CMD ["python", "-c", "import crosswalk"]
