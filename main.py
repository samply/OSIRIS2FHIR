import logging
from logging_setup import setup_logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from etl import run_etl

setup_logging()
log = logging.getLogger(__name__)

osiris2fhir = FastAPI(title="OSIRIS2FHIR", version="0.1.0")


@osiris2fhir.get("/health")
def health():
    return {"status": "ok"}


@osiris2fhir.post("/import")
async def importer_import(request: Request):
    input = await request.json()

    response = run_etl(input)
    return response