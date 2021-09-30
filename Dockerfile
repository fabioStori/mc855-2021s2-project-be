FROM python:3.8

MAINTAINER InventIO
EXPOSE 4000
COPY src .
COPY requirements.txt .


RUN pip install -r requirements.txt

CMD ["python","app.py"]