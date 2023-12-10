FROM python:3.10.12

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY app/* /app

ENTRYPOINT [ "uvicorn" ]

CMD ["main:app", "--host", "0.0.0.0", "--port", "8008"]
