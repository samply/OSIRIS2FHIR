import logging
from logging_setup import setup_logging
from fastapi import FastAPI, Request, HTTPException
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

    try:
        return run_etl(input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="internal error")