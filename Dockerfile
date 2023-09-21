FROM python:3

WORKDIR /usr/src/babyapp

COPY requirements.txt requirements.txt
COPY main.py main.py  

RUN pip install -r requirements.txt
CMD ["python", "main.py"]
