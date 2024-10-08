# FROM python
FROM python:3.9


WORKDIR /usr/src/app

COPY req.txt ./

RUN pip install -r req.txt
