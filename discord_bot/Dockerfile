# Build from the REPO ROOT so the bot can read academy/ content:
#   docker build -f discord_bot/Dockerfile -t vllm-academy-bot .
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends fonts-noto-cjk fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY discord_bot/requirements.txt discord_bot/requirements.txt
RUN pip install --no-cache-dir -r discord_bot/requirements.txt
COPY academy/ academy/
COPY phase1/ phase1/
COPY course/ course/
COPY labs/ labs/
COPY templates/ templates/
COPY ROADMAP.md README.md ./
COPY discord_bot/ discord_bot/
ENV ACADEMY_DB_PATH=/data/academy.sqlite3 PYTHONUNBUFFERED=1
VOLUME ["/data"]
WORKDIR /app/discord_bot
RUN python -m academy_bot --check
CMD ["python", "-m", "academy_bot"]
