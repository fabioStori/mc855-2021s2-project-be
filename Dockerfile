FROM python:3.8

MAINTAINER InventIO
EXPOSE 4000

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src .

CMD ["python","app.py"]