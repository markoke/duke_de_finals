FROM python:3.11-alpine

WORKDIR /airqo

COPY ./requirements.txt /airqo/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /airqo/requirements.txt

COPY ./app /airqo/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]