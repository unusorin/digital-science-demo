FROM python:3.9

ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0","--reload"]