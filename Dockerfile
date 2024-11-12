FROM python:3.12

RUN mkdir /code
COPY requirements.txt /code
RUN pip install --upgrade setuptools
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt --no-cache-dir
COPY . /code
WORKDIR /code
