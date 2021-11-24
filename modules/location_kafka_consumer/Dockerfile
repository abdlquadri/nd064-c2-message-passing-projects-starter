FROM ubuntu:bionic

WORKDIR .

RUN apt-get update
RUN apt-get install python3 python3-pip -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD ["python3", "app/udaconnect/services.py"]