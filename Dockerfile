FROM python:3.7-alpine

WORKDIR /app

COPY komponents komponents
COPY setup.py .

RUN pip install .

ENTRYPOINT ["komponents"]
