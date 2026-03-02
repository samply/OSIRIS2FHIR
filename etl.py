from transformation import run_transformation
import urllib.request
import urllib.error

def run_etl(input):
    fhir_xml  = run_transformation(input)
    return load(fhir_xml)


def load(fhir_xml: str) -> dict:
    url = "http://blaze:8080/fhir"

    request = urllib.request.Request(
        url,
        data=fhir_xml.encode("utf-8"),
        headers={"Content-Type": "application/fhir+xml", "Accept": "application/fhir+xml"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.getcode()
            body_text = response.read().decode("utf-8", errors="replace")
            return {"status": status, "headers": dict(response.headers.items()), "body": body_text}

    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        headers = dict(exc.headers.items()) if exc.headers else {}
        print(f"FHIR POST failed: {exc.code} {exc.reason}")
        if headers.get("Location"):
            print(f"Location: {headers['Location']}")
        if body_text:
            print(body_text)
        return {"status": exc.code, "headers": headers, "body": body_text, "error": f"{exc.code} {exc.reason}"}

    except urllib.error.URLError as exc:
        print(f"FHIR POST connection error: {exc.reason}")
        return {"status": None, "headers": {}, "body": "", "error": str(exc.reason)}