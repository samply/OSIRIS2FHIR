import uuid
import logging
import re
from datetime import date
from hashlib import sha256
import os
SALT = os.getenv("SALT", "")
PROFILE = os.getenv("FHIR_PROFILE", "pscc").lower()
if PROFILE == "pscc":
    from transformationTemplates_pscc import (
        get_Patient, get_Observation_Vitalstatus, get_Condition, get_Observation_Histology, get_Observation_UICC, get_MedicationStatement
    )
elif PROFILE == "cce":
    from transformationTemplates_cce import (
        get_Patient, get_Observation_Vitalstatus, get_Condition, get_Observation_Histology, get_Observation_UICC, get_MedicationStatement, get_Specimen, get_Procedure
    )
else:
    raise ValueError(f"unknown FHIR_PROFILE: {PROFILE}")
from constants import TNM_ALLOWED, SPECIMEN_MAP

log = logging.getLogger(__name__)
FHIR_DATE_RE = re.compile(r"\d{4}(-\d{2}(-\d{2})?)?$")
ICD10_RE = re.compile(r"[CD]\d{2}(\.\d)?$")
ICDO3_MORPH_RE = re.compile(r"^\d{4}/\d$")

def run_transformation(input_list):
    bundle_id = str(uuid.uuid4())
    bundle=[f'<Bundle xmlns="http://hl7.org/fhir">\n\t<id value="{bundle_id}"/>\n\t<type value="batch"/>']
    counter=0
    duplicate = set()
    for input in input_list:
        counter+=1
        log.info(f"transforming Patient {counter} to fhir bundle")
        ###Patient    
        patient_identifier = input.get("patientId")
        patient_id=hash_value(patient_identifier)
        birth_date = get_valid_date(input.get("birthdateYear"),input.get("birthdateMonth"),input.get("birthdateDay"))
        biologicalSex = (input.get("biologicalSex") or "unknown").strip().lower()
        biologicalSex = biologicalSex if biologicalSex in ("male", "female") else "unknown"
        bundle.append(get_Patient(patient_id,patient_identifier,birth_date,biologicalSex))

        ###Vitalstatus
        log.debug('creating vitalstatus Observation')
        latest_news = input.get("latestNews") or {}
        vitalstatus = (latest_news.get("vitalStatus") or "").strip().lower()
        vitalstatus_date = latest_date_helper(latest_news)
        if not vitalstatus and get_valid_date(latest_news.get("deathDateYear")):vitalstatus = "deceased"
        if not vitalstatus and vitalstatus_date: vitalstatus = "alive"
        if vitalstatus in ("alive", "dead", "deceased"):
            vitalstatus_value = "deceased" if vitalstatus != "alive" else "alive"
            obs_id=hash_value(patient_id)
            bundle.append(get_Observation_Vitalstatus(obs_id,patient_id,vitalstatus_value,vitalstatus_date))
        else:
            log.warn(f'Patient "{patient_identifier}" has no vitalstatus information (vitalStatus)')



        ###Condition
        diagnoses = input.get("primaryCancer") or {}
        #iterate through all conditions
        condition_id="" #TODO find a way to link other children to condition
        for diagnosis in diagnoses:
            log.debug('creating diagnosis Condition')
            diagnosis_icdo3 = diagnosis.get("topographyCode")
            diagnosis_icd10 = diagnosis_icdo3 #TODO replace in next iteration
            diagnosis_icdo3_text = diagnosis.get("topographyGroup")
            diagnosis_date = get_valid_date(diagnosis.get("cancerDiagnosisDateYear"),diagnosis.get("cancerDiagnosisDateMonth"),diagnosis.get("cancerDiagnosisDateDay"))
            condition_id = hash_value(str(patient_id)+str(diagnosis_date)+str(diagnosis_icd10))
            laterality = map_laterality(diagnosis.get("laterality"))
            if is_fhir_date(diagnosis_date) and is_icd10_code(diagnosis_icd10):
                log.info(f'everything in condition present "{diagnosis_icd10}"')
                bundle.append(get_Condition(condition_id,diagnosis_icd10,diagnosis_icdo3,patient_id,diagnosis_date,diagnosis_icdo3_text,laterality))
            else:
                log.error(f'Patient "{patient_identifier}" has incorrect Condition "{diagnosis_icdo3}" or diagnosis date "{diagnosis_date}" (topographyCode;cancerDiagnosisDateYear)')
                raise ValueError(f'ERROR: Patient "{patient_identifier}" has incorrect Condition "{diagnosis_icdo3}" or diagnosis date "{diagnosis_date}" (topographyCode;cancerDiagnosisDateYear)')


            ###Histology
            log.debug('creating histology Observation')
            histology_value = diagnosis.get("morphologyCode")
            obs_id = hash_value(str(patient_id)+str(condition_id)+str(histology_value))
            if is_icdo3_morphology(histology_value):
                bundle.append(get_Observation_Histology(obs_id,patient_id,condition_id,diagnosis_date,histology_value))
            else:
                log.warn(f'Patient "{patient_identifier}" has incorrect Histology "{histology_value}" (morphologyCode)')

            ###TNM / UICC
            log.debug('creating TNM Observation')
            tnms = diagnosis.get("tnmEvent") or {}
            for tnm in tnms:
                tnm_prefix = tnm.get("tnmType")
                tnm_t = map_tnm(pick(tnm, "tValue", "t", "T"), "t")
                tnm_n = map_tnm(pick(tnm, "nValue", "n", "N"), "n")
                tnm_m = map_tnm(pick(tnm, "mValue", "m", "M"), "m")
                uicc_stage = uicc_heuristic_stage(tnm_t, tnm_n, tnm_m)
                obs_id=hash_value(str(patient_id)+str(condition_id)+str(uicc_stage)+str(tnm_t)+str(tnm_n)+str(tnm_m))
                bundle.append(get_Observation_UICC(obs_id,patient_id,condition_id,uicc_stage,tnm_prefix,tnm_t,tnm_n,tnm_m))

            #Surgery
            log.debug('creating Surgery Procedure')
            surgeries = diagnosis.get("surgery") or []
            for surgery in surgeries:
                prod_start = get_valid_date(surgery.get("surgeryDateYear"),surgery.get("surgeryDateMonth"),surgery.get("surgeryDateDay"))
                prod_end = "" #TODO
                if prod_start:
                    log.debug('test3')
                    prod_id=hash_value(str(patient_id)+str(condition_id)+str(prod_start)+"OP")
                    bundle.append(get_Procedure("OP",prod_id,patient_id,condition_id,prod_start,prod_end)) if not prod_id in duplicate else log.warn(f'Patient "{patient_id}" has duplicate surgery')
                    duplicate.add(prod_id)
                else:
                    log.warn(f'Patient "{patient_id}" has incorrect Surgery "{prod_start}" (surgeryDate)')

            #Radiotherapy
            log.debug('creating Radiotherapy Procedure')
            radiotherapies = diagnosis.get("radiotherapy") or []
            for radiotherapy in radiotherapies:
                prod_start = get_valid_date(radiotherapy.get("radiationDateYear"),radiotherapy.get("radiationDateMonth"),radiotherapy.get("radiationDateDay"))
                prod_end = "" #TODO
                if prod_start:
                    prod_id=hash_value(str(patient_id)+str(condition_id)+str(prod_start)+"RT")
                    bundle.append(get_Procedure("RT",prod_id,patient_id,condition_id,prod_start,prod_end)) if not prod_id in duplicate else log.warn(f'Patient "{patient_id}" has duplicate radiotherapy')
                    duplicate.add(prod_id)
                else:
                    log.warn(f'Patient "{patient_id}" has incorrect Radiotherapy "{prod_start}" (radiationDate)')
        #Biomarker
        #markers = diagnosis.get("tnmEvent") or {}

        #Specimen
        log.debug('creating Specimen')
        specimina  = input.get("biologicalSpecimen") or {}
        for specimen in specimina:
            specimen_type = map_specimen_type(specimen.get("specimenType"),specimen.get("specimenNature"))
            specimen_date = get_valid_date(specimen.get("biologicalSpecimenCollectDateYear"),specimen.get("biologicalSpecimenCollectDateMonth"),specimen.get("biologicalSpecimenCollectDateDay"))
            specimen_id = hash_value(str(patient_id)+str(specimen_type)+str(specimen_date))
            bundle.append(get_Specimen(specimen_id,patient_id,specimen_type,specimen_date))



        #Medication
        log.debug('creating SYST MedicationStatement')
        medications = input.get("medication") or {}
        for medication in medications:
            atc_code = medication.get("moleculeCode")
            atc_text = medication.get("moleculeName")
            med_therapy = map_atc_to_therapy(atc_code)
            med_date = get_valid_date(medication.get("moleculeDateYear"),medication.get("moleculeDateMonth"),medication.get("moleculeDateDay"))
            med_date_end = get_valid_date(medication.get("moleculeEndDateYear"),medication.get("moleculeEndDateMonth"),medication.get("moleculeEndDateDay"))
            med_id=hash_value(str(patient_id)+str(condition_id)+str(med_therapy)+str(med_date))
            bundle.append(get_MedicationStatement(med_id,patient_id,condition_id,atc_code,atc_text,med_therapy,med_date,med_date_end))

        #Surgery
        log.debug('creating Surgery Procedure (outer loop)')
        procedures = input.get("surgery") or []
        for procedure in procedures:
            prod_start = get_valid_date(procedure.get("surgeryDateYear"),procedure.get("surgeryDateMonth"),procedure.get("surgeryDateDay"))
            prod_end = "" #TODO
            if prod_start:
                prod_id=hash_value(str(patient_id)+str(condition_id)+str(prod_start)+"OP")
                bundle.append(get_Procedure("OP",prod_id,patient_id,condition_id,prod_start,prod_end)) if not prod_id in duplicate else log.warn(f'Patient "{patient_id}" has duplicate surgery')
                duplicate.add(prod_id)
            else:
                log.warn(f'Patient "{patient_id}" has incorrect Surgery "{prod_start}" (surgeryDateYear)')
        #Radiotherapy
        log.debug('creating Radiotherapy Procedure (outer loop)')
        radiotherapies = input.get("radiotherapy") or []
        for radiotherapy in radiotherapies:
            prod_start = get_valid_date(radiotherapy.get("radiationDateYear"),radiotherapy.get("radiationDateMonth"),radiotherapy.get("radiationDateDay"))
            prod_end = "" #TODO
            if prod_start:
                prod_id=hash_value(str(patient_id)+str(condition_id)+str(prod_start)+"RT")
                bundle.append(get_Procedure("RT",prod_id,patient_id,condition_id,prod_start,prod_end)) if not prod_id in duplicate else log.warn(f'Patient "{patient_id}" has duplicate radiotherapy')
                duplicate.add(prod_id)
            else:
                log.warn(f'Patient "{patient_id}" has incorrect Radiotherapy "{prod_start}" (radiationDate)')

            
    
    bundle.append("</Bundle>")
    return '\n'.join(bundle)



def hash_value(value):
    return sha256(f'{value}{SALT}'.encode('utf-8')).hexdigest()[:15]

def is_fhir_date(value: str) -> bool:
    return bool(value) and bool(FHIR_DATE_RE.fullmatch(value))

def is_icd10_code(value: str) -> bool:
    return bool(value) and bool(ICD10_RE.fullmatch(value))

def is_icdo3_morphology(value: str) -> bool:
    return bool(value) and bool(ICDO3_MORPH_RE.fullmatch(value))

def get_valid_date(year=None, month=None, day=None):
    log.debug(f"year {year}, month {month}, day {day}")
    year = f"{int(year):04d}" if year not in (None, "") else None
    return None if year is None else year + (f"-{int(month):02d}" if month not in (None, "") else "") + (f"-{int(day):02d}" if month not in (None, "") and day not in (None, "") else "")

def get_latest_date(dates):
    return max((d for d in dates if d), default=None)

def latest_date_helper(latest_news):
    date1 = get_valid_date(
        latest_news.get("vitalStatusUpdateDateYear"),
        latest_news.get("vitalStatusUpdateDateMonth"),
        latest_news.get("vitalStatusUpdateDateDay"),
    )
    date2 = get_valid_date(
        latest_news.get("latestVisitDateYear"),
        latest_news.get("latestVisitDateMonth"),
        latest_news.get("latestVisitDateDay"),
    )
    date3 = get_valid_date(
        latest_news.get("lastContactDateYear"),
        latest_news.get("lastContactDateMonth"),
        latest_news.get("lastContactDateDay"),
    )
    date4 = get_valid_date(
        latest_news.get("deathDateYear"),
        latest_news.get("deathDateMonth"),
        latest_news.get("deathDateDay"),
    )
    return get_latest_date([date1, date2, date3, date4])

def map_atc_to_therapy(atc):
    a = (atc or "").upper()
    if a.startswith(("H","L02","G03")): return "HO"
    if a.startswith(("L01XC","L01X","L03","L04")): return "IM"
    if a.startswith(("L01E","L01XX")): return "ZS"
    if a.startswith("L01"): return "CH"
    return "SO"

def uicc_heuristic_stage(t, n, m):
    if not (t and n and m) or "X" in (t, n, m): return "X"
    if m[0] == "1": return "IV"
    if t.startswith("is"): return "0"
    if n[0] in "23": return "III"
    if n[0] == "1": return "III" if t[0] in "34" else "II"
    return "II" if t[0] in "234" else "I" if t[0] in "01" else "X"

def map_laterality(value):
    v = (value or "").strip().lower()
    if not v:
        return None
    return {
        "l": "L", "left": "L",
        "r": "R", "right": "R",
        "b": "B", "bilateral": "B",
        "c": "C", "center": "C", "centerline": "C",
        "n": "N", "not applicable": "N", "not-applicable": "N",
        "u": "U", "unknown": "U",
    }.get(v, "U")

def map_tnm(value, kind):
    v = (value or "").strip()
    if not v:
        return None
    # "T1a" -> "1a"
    if v[:1].upper() in "TNM":
        v = v[1:].strip()

    allowed = TNM_ALLOWED.get((kind or "").strip().lower())
    if allowed and v in allowed:
        log.debug(f'TNM value "{value}" has been set to "{v}"')
        return v
    else:
        log.warn(f'TNM value "{value}" has been set to "X"')
        return "X"

# temporary function to harmonize different OSIRIS RWD formats
def pick(d: dict, *keys, default=None):
    for k in keys:
        v = d.get(k)
        if v not in (None, "", []):
            return v
    return default

def map_specimen_type(specimen_type=None, specimen_nature=None, default="derivative-other"):
    text = f"{specimen_type or ''} {specimen_nature or ''}".lower()
    for code, keywords in SPECIMEN_MAP:
        if any(n in text for n in keywords):
            return code
    return default