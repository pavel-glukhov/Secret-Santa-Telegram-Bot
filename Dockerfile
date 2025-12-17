FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt /code
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt --no-cache-dir

COPY . /code

CMD ["python", "-m", "app.runtimes.polling"]
