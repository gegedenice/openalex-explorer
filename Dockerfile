# syntax=docker/dockerfile:1
FROM python:3.12-slim
RUN apt-get update \ 
    && apt-get install -y git curl vim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#VOLUME ["/app"]
EXPOSE 5000
CMD [ "gunicorn", "--bind=0.0.0.0:5000", "--timeout=0", "wsgi:app"]