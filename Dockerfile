FROM python:3.12-slim

WORKDIR /gr_osiris2fhir

RUN pip install fastapi uvicorn

COPY main.py ./

EXPOSE 8080

CMD ["uvicorn", "main:gr_osiris2fhir", "--host", "0.0.0.0", "--port", "8080"]
