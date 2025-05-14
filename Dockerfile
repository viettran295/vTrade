FROM ubuntu:24.04

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

WORKDIR /app

ADD . .

RUN uv python install 3.11

RUN uv sync --locked 

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8050

CMD ["/app/.venv/bin/gunicorn", "--bind", "0.0.0.0:8050", "app:server"]