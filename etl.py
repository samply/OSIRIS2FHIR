from transformation import run_transformation
import urllib.request

def run_etl(input):
    fhir_xml  = run_transformation(input)
    return load(fhir_xml)


def load(fhir_xml):
    url = "http://blaze:8080/fhir"
    request = urllib.request.Request(
        url,
        data=fhir_xml.encode("utf-8"),
        headers={"Content-Type": "application/fhir+xml"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()
