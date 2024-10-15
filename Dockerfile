# Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y \
    build-essential \
    curl

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the static directory exists
RUN mkdir -p static

CMD ["python", "app.py"]