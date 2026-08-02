# Start from an official Python image. The "slim" variant drops build tools
# and docs we don't need at runtime - roughly 150MB instead of 1GB.
FROM python:3.12-slim

# Where our code lives inside the container.
WORKDIR /app

# Copy requirements FIRST, before the application code.
#
# This ordering is the single most important thing in this file. Docker caches
# each instruction as a layer and reuses the cache until something changes.
# Dependencies change rarely; your code changes constantly. Copying
# requirements separately means editing main.py doesn't force a full
# reinstall of FastAPI on every rebuild.
COPY requirements.txt .

# --no-cache-dir keeps pip from squirreling away wheels we'll never reuse,
# which would bloat the image for no benefit.
RUN pip install --no-cache-dir -r requirements.txt

# Now the application code. This layer rebuilds on every code change - which
# is fine, because it's small.
COPY app/ ./app/

# Run as a non-root user.
#
# By default containers run as root. If an attacker finds a way to execute
# code in your container, root inside the container is a much better starting
# position than an unprivileged account. This is cheap to do and worth doing.
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Documents which port the app listens on. Does not actually publish it -
# that's done at run time with -p. This line is for humans and tooling.
EXPOSE 8000

# Bind to 0.0.0.0, not 127.0.0.1.
#
# 127.0.0.1 inside a container means "only reachable from inside this
# container" - the port mapping would appear to work and nothing would
# respond. This catches people out constantly.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

