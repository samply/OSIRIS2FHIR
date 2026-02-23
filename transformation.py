import uuid
from datetime import date
from hashlib import sha256
from transformationTemplates import get_Patient, get_Observation_Vitalstatus

def hash_value(value):
    return sha256(value.encode('utf-8')).hexdigest()[:15]

def get_valid_date(year=None, month=""):
    if year in (None, ""):
        return ""

    y = int(year)
    if not (1900 <= y <= date.today().year):
        return ""

    if month in (None, ""):
        return str(y)

    m = int(month)
    return f"{y}-{m:02d}" if 1 <= m <= 12 else str(y)

def run_transformation(input):
    body = input.get("BODY", {})
    bundle_id = str(uuid.uuid4())
    bundle=[f'<Bundle xmlns="http://hl7.org/fhir">\n\t<id value="{bundle_id}"/>\n\t<type value="transaction"/>']
    
    ###Patient    
    patient_identifier = body.get("patientId")
    patient_id=hash_value(patient_identifier)
    birth_date = get_valid_date(body.get("birthdateYear"),body.get("birthdateMonth"))
    biologicalSex = body.get("biologicalSex")
    bundle.append(get_Patient(patient_id,patient_identifier,birth_date,biologicalSex))

    ###Vitalstatus
    latest_news = body.get("latestNews") or {}
    obs_id=hash_value(patient_id)
    vitalstatus_value = "deceased" if latest_news.get("vitalStatus")=="Dead" else "alive"
    vitalstatus_date = get_valid_date(latest_news.get("vitalStatusUpdateDateYear"),latest_news.get("vitalStatusUpdateDateMonth"))

    bundle.append(get_Observation_Vitalstatus(obs_id,patient_id,vitalstatus_value,vitalstatus_date))
    #bundle.append(get_Condition(condition_id,diagnosis_icd10,diagnosis_icdo3,patient_id,diagnosis_date))
    
    return '\n'.join(bundle)