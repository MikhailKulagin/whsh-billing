FROM python:latest

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .. .

CMD ["python3", "./service.py"]