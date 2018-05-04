FROM python:3.6

ENV PYTHONUNBUFFERED 1

COPY ./* /justdoist/

WORKDIR /justdoist/

MKDIR static

RUN pip install -r requirements.txt

EXPOSE 8000
