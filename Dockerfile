FROM debian:bullseye-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

WORKDIR /app

ADD . .

RUN uv python install 3.11 && uv sync --locked 

EXPOSE 8050

CMD ["/app/.venv/bin/gunicorn", "--workers=2", "--bind", "0.0.0.0:8050", "app:server"]
