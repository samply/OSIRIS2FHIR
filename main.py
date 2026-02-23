from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse

from etl import run_etl

gr_osiris2fhir = FastAPI(title="OSIRIS2FHIR", version="0.1.0")


@gr_osiris2fhir.get("/health")
def health():
    return {"status": "ok"}


@gr_osiris2fhir.post("/import", status_code=201)
async def importer_import(request: Request):
    input = await request.json()

    result = run_etl(input)

    return JSONResponse(
        {
            "status": "ok",
            "result": result
        }
    )
