FROM python:3.7-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

ENV DB_ENGINE ${{ secrets.DB_ENGINE }}
ENV DB_NAME ${{ secrets.DB_NAME }}
ENV POSTGRES_USER ${{ secrets.POSTGRES_USER }}
ENV POSTGRES_PASSWORD ${{ secrets.POSTGRES_PASSWORD }}
ENV DB_HOST ${{ secrets.DB_HOST }}
ENV DB_PORT ${{ secrets.DB_PORT }}
ENV ALLOWED_HOST_1 ${{ secrets.ALLOWED_HOST_1 }}
ENV ALLOWED_HOST_2 ${{ secrets.ALLOWED_HOST_2 }}
ENV ALLOWED_HOST_3 ${{ secrets.ALLOWED_HOST_3 }}
ENV ALLOWED_HOST_4 ${{ secrets.ALLOWED_HOST_4 }}

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
