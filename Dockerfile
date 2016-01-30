FROM python:2.7.10
ADD . /dpsht
WORKDIR /dpsht
RUN pip install -r requirements.txt
