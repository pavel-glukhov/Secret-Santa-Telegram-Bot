FROM python:3.10

RUN mkdir /code
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt --no-cache-dir
COPY . /code
WORKDIR /code
