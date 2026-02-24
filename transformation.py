import uuid
from datetime import date
from hashlib import sha256
from transformationTemplates import get_Patient, get_Observation_Vitalstatus, get_Condition, get_Observation_Histology, get_Observation_UICC

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
    bundle.append(get_Observation_Vitalstatus(obs_id,patient_id,vitalstatus_value,vitalstatus_date))#TODO trow error on missing element

    ###Condition
    diagnoses = body.get("primaryCancer") or {}
    #iterate through all conditions
    for diagnosis in diagnoses:
        diagnosis_date=get_valid_date(diagnosis.get("cancerDiagnosisDateYear"),diagnosis.get("cancerDiagnosisDateMonth"))
        diagnosis_icd10=diagnosis.get("topographyCode")
        diagnosis_icdo3=diagnosis.get("topographyGroup")
        condition_id=hash_value(str(patient_id)+str(diagnosis_date)+str(diagnosis_icd10))
        bundle.append(get_Condition(condition_id,diagnosis_icd10,diagnosis_icdo3,patient_id,diagnosis_date))#TODO trow error on missing element

        ###Histology
        histology_value=diagnosis.get("morphologyCode")
        obs_id=hash_value(str(patient_id)+str(condition_id)+str(histology_value))
        bundle.append(get_Observation_Histology(obs_id,patient_id,diagnosis_date,histology_value))#TODO trow error on missing element

        ###TNM / UICC
        tnms = diagnosis.get("tnmEvent") or {}
        for tnm in tnms:
            tnm_date = tnm.get("TODO")
            uicc_stage = tnm.get("TODO")
            tnm_prefix = tnm.get("tnmType")
            tnm_t = tnm.get("tValue")
            tnm_n = tnm.get("nValue")
            tnm_m = tnm.get("mValue")
            obs_id=hash_value(str(patient_id)+str(condition_id)+str(uicc_stage)+str(tnm_t)+str(tnm_n)+str(tnm_m))
            bundle.append(get_Observation_UICC(obs_id,patient_id,condition_id,tnm_date,uicc_stage,tnm_prefix,tnm_t,tnm_n,tnm_m))
    
    return '\n'.join(bundle)