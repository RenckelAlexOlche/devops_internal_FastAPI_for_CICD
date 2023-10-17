FROM python:3.10

ENV MYSQL_USER $MYSQL_USER
ENV MYSQL_PASSWORD $MYSQL_PASSWORD
ENV MYSQL_HOST $MYSQL_HOST
ENV MYSQL_PORT $MYSQL_PORT
ENV MYSQL_DB $MYSQL_DB
ENV JWT_SECRET $JWT_SECRET

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

#RUN alembic -c app/alembic.ini stamp head

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
