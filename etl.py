from transformation import run_transformation
#import os, urllib.request

def run_etl(input):
    fhir_xml  = run_transformation(input)
    load(fhir_xml)


def load(fhir_xml):
    print(fhir_xml)

    # fhir_base_url = os.environ.get("FHIR_BASE_URL", "").rstrip("/")
    # if not fhir_base_url:
    #     return
    #
    # url = fhir_base_url + "/"
    # request = urllib.request.Request(
    #     url,
    #     data=fhir_xml.encode("utf-8"),
    #     headers={"Content-Type": "application/fhir+xml"},
    #     method="POST",
    # )
    # with urllib.request.urlopen(request, timeout=15) as response:
    #     response.read()
