FROM python:3.10-bullseye


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps:
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    wget \
  # Cleaning cache:
  && pip3 install poetry

# set work directory
WORKDIR /usr/src/app
COPY pyproject.toml poetry.lock /usr/src/app/

# Install dependencies:
RUN poetry install
# copy project
COPY . .
