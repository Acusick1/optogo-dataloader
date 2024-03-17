FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements ./requirements

RUN pip install --no-cache-dir -r requirements/prod.txt

ENV PYTHONPATH ./

COPY main.py ./
COPY config.py ./
COPY logging.ini ./

COPY loader ./loader
COPY shared ./shared

CMD ["python", "main.py"]