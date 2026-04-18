FROM debian:stable-slim@sha256:e51bfcd2226c480a5416730e0fa2c40df28b0da5ff562fc465202feeef2f1116

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -G appgroup -m appuser
USER appuser

WORKDIR /app
COPY --chown=appuser:appgroup . .

RUN uv python install 3.13 && \
    uv sync --locked --no-cache

EXPOSE 8050
CMD ["/app/.venv/bin/gunicorn", "--workers=2" ,"--threads=4", "--bind", "0.0.0.0:8050", "app:server"]