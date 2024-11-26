# app/Dockerfile

FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

#RUN git clone https://github.com/dorianganessa/dati-immobiliari.git .

RUN uv sync --frozen
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["uv","run","streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]