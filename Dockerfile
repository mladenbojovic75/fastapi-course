FROM python:3.12-alpine AS base


# Create python virtual environment adn install dependencies in it
WORKDIR /home/fastapi/

RUN apk update && \
    apk add --no-cache postgresql-libs \
    --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev 

RUN python3 -m venv /home/fastapi/venv

ENV PATH="/home/fastapi/venv/bin:$PATH"

RUN --mount=source=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt



# Build stage - copy files from base and reduce image size
FROM python:3.12-alpine AS build
ARG UID=5000
ARG GID=5000
ARG HOST="0.0.0.0"
ARG PORT=8000
ARG ROOT_PATH="/"
ENV HOST=$HOST
ENV PORT=$PORT
ENV ROOT_PATH=$ROOT_PATH
RUN addgroup --gid $GID fastapi && \
    adduser --ingroup fastapi -u $UID --system -s /bin/sh fastapi && \
    mkdir "/home/fastapi/app" && chown fastapi:fastapi "/home/fastapi/app"


# Install missing lib to run psycopg2
# Copy python libs and app source
RUN apk update && \
    apk add --no-cache libpq vim

COPY --from=base --chown=fastapi:fastapi /home/fastapi/venv /home/fastapi/venv
COPY --chown=fastapi:fastapi app/ /home/fastapi/app

ENV PATH="$PATH:/home/fastapi/venv/bin"
RUN echo "export PATH=$PATH" >> /etc/profile

USER fastapi
WORKDIR /home/fastapi
ENTRYPOINT ["/bin/sh", "-c", "uvicorn app.main:app --host ${HOST} --port ${PORT} --root-path ${ROOT_PATH}"]
