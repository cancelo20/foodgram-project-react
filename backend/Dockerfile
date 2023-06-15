FROM python:3.7-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

ENV DB_ENGINE os.getenv('DB_ENGINE')
ENV DB_NAME os.getenv('DB_NAME')
ENV POSTGRES_USER os.getenv('POSTGRES_USER')
ENV POSTGRES_PASSWORD os.getenv('POSTGRES_PASSWORD')
ENV DB_HOST os.getenv('DB_HOST')
ENV DB_PORT os.getenv('DB_PORT')
ENV ALLOWED_HOST_1 os.getenv('ALLOWED_HOST_1')
ENV ALLOWED_HOST_2 os.getenv('ALLOWED_HOST_2')
ENV ALLOWED_HOST_3 os.getenv('ALLOWED_HOST_3')
ENV ALLOWED_HOST_4 os.getenv('ALLOWED_HOST_4')

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
