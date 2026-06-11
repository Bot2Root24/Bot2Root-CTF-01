FROM python:3.11-slim

WORKDIR /app
COPY app.py .
RUN pip install flask

EXPOSE 80

CMD ["python3", "app.py"]
