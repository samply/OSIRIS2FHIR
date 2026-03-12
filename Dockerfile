FROM python:3.12-slim

WORKDIR /osiris2fhir

RUN pip install fastapi uvicorn datetime

COPY *.py ./

EXPOSE 8080

CMD ["uvicorn", "main:osiris2fhir", "--host", "0.0.0.0", "--port", "8080"]
