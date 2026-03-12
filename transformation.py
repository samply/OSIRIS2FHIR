import uuid
from datetime import date
from hashlib import sha256
from transformationTemplates import get_Patient, get_Observation_Vitalstatus, get_Condition, get_Observation_Histology, get_Observation_UICC, get_MedicationStatement

def hash_value(value):
    return sha256(value.encode('utf-8')).hexdigest()[:15]

def get_valid_date(year=None, month=None, day=None):
    year = f"{int(year):04d}" if year not in (None, "") else None
    return None if year is None else year + (f"-{int(month):02d}" if month not in (None, "") else "") + (f"-{int(day):02d}" if month not in (None, "") and day not in (None, "") else "")

def run_transformation(input_list):
    bundle_id = str(uuid.uuid4())
    bundle=[f'<Bundle xmlns="http://hl7.org/fhir">\n\t<id value="{bundle_id}"/>\n\t<type value="batch"/>']
    for input in input_list:
        ###Patient    
        patient_identifier = input.get("patientId")
        patient_id=hash_value(patient_identifier)
        birth_date = get_valid_date(input.get("birthdateYear"),input.get("birthdateMonth"),input.get("birthdateDay"))
        biologicalSex = (input.get("biologicalSex") or "unknown").strip().lower()
        biologicalSex = biologicalSex if biologicalSex in ("male", "female", "unknown") else "unknown"
        bundle.append(get_Patient(patient_id,patient_identifier,birth_date,biologicalSex))

        ###Vitalstatus
        latest_news = input.get("latestNews") or {}
        obs_id=hash_value(patient_id)
        vitalstatus_value = "deceased" if latest_news.get("vitalStatus")=="Dead" else "alive"
        vitalstatus_date = get_valid_date(latest_news.get("vitalStatusUpdateDateYear"),latest_news.get("vitalStatusUpdateDateMonth"))
        bundle.append(get_Observation_Vitalstatus(obs_id,patient_id,vitalstatus_value,vitalstatus_date))#TODO trow error on missing element

        ###Condition
        diagnoses = input.get("primaryCancer") or {}
        #iterate through all conditions
        condition_id="" #TODO find a way to link other children to condition
        for diagnosis in diagnoses:
            diagnosis_date = get_valid_date(diagnosis.get("cancerDiagnosisDateYear"),diagnosis.get("cancerDiagnosisDateMonth"))
            diagnosis_icd10 = diagnosis.get("topographyCode")
            diagnosis_icdo3 = diagnosis.get("topographyGroup")
            condition_id = hash_value(str(patient_id)+str(diagnosis_date)+str(diagnosis_icd10))
            bundle.append(get_Condition(condition_id,diagnosis_icd10,diagnosis_icdo3,patient_id,diagnosis_date))#TODO trow error on missing element

            ###Histology
            histology_value = diagnosis.get("morphologyCode")
            obs_id = hash_value(str(patient_id)+str(condition_id)+str(histology_value))
            bundle.append(get_Observation_Histology(obs_id,patient_id,diagnosis_date,histology_value))#TODO trow error on missing element

            ###TNM / UICC
            tnms = diagnosis.get("tnmEvent") or {}
            for tnm in tnms:
                tnm_date = tnm.get("TODO")
                tnm_prefix = tnm.get("tnmType")
                tnm_t = tnm.get("tValue")
                tnm_n = tnm.get("nValue")
                tnm_m = tnm.get("mValue")
                uicc_stage = uicc_heuristic_stage(tnm_t, tnm_n, tnm_m)#tnm.get("TODO")
                obs_id=hash_value(str(patient_id)+str(condition_id)+str(uicc_stage)+str(tnm_t)+str(tnm_n)+str(tnm_m))
                bundle.append(get_Observation_UICC(obs_id,patient_id,condition_id,tnm_date,uicc_stage,tnm_prefix,tnm_t,tnm_n,tnm_m))
            
        #Biomarker TODO
        #markers = diagnosis.get("tnmEvent") or {}

        #Medication
        #medications = input.get("medication") or {}
        #for medication in medications:
            #atc_code = medication.get("moleculeCode")
            #atc_text = medication.get("moleculeName")
            #med_therapy = map_atc_to_therapy(atc_code)
            #med_date = get_valid_date(medication.get("moleculeDateYear"),medication.get("moleculeDateMonth"))
            #med_date_end = get_valid_date(medication.get("moleculeEndDateYear"),medication.get("moleculeEndDateMonth")) # TODO missing elements in GR
            #med_id=hash_value(str(patient_id)+str(condition_id)+str(med_therapy)+str(med_date))
            #bundle.append(get_MedicationStatement(med_id,patient_id,condition_id,atc_code,atc_text,med_therapy,med_date,med_date_end))
    
    bundle.append("</Bundle>")
    return '\n'.join(bundle)

def map_atc_to_therapy(atc):
    a = (atc or "").upper()
    if a.startswith(("H","L02","G03")): return "HO"
    if a.startswith(("L01XC","L01X","L03","L04")): return "IM"
    if a.startswith(("L01E","L01XX")): return "ZS"
    if a.startswith("L01"): return "CH"
    return "SO"

def uicc_heuristic_stage(t, n, m):
    t=(t or "").upper(); n=(n or "").upper(); m=(m or "").upper()

    if m in ("M1","M1A","M1B","M1C"): return "IV"
    if "X" in (t+n+m) or not (t and n and m): return "X"

    if t in ("TIS",): return "0"

    if n in ("N3","N2"): return "III"
    if n == "N1": return "III" if t in ("T3","T4") else "II"

    if t in ("T4","T3"): return "II"
    if t in ("T2",): return "II"
    if t in ("T1","T0"): return "I"

    return "X"