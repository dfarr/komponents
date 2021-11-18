FROM python:3.7

COPY komponents komponents
COPY setup.py .

RUN pip install .

ENTRYPOINT ["komponents"]
