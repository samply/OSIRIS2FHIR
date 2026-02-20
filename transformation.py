import uuid
from hashlib import sha256

def hash_value(value):
    return sha256(value.encode('utf-8')).hexdigest()[:15]
    

def get_Patient(patient_id,birth_date,biologicalSex):
    return (f'''
        <entry>
            <fullUrl value="PSCC/Patient/{patient_id}"/>
            <resource>
                <Patient>
                    <id value="{patient_id}"/>
                    <meta>
                        <profile value="https://simplifier.net/PSCC/StructureDefinition-PSCC-Patient"/>
                    </meta>
                    <identifier>
                        <value value="{hash_value(patient_id)}"/>
                    </identifier>
                    <gender value="{biologicalSex}"/>
                    <birthDate value="{birth_date}"/>
                </Patient>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Patient/{patient_id}"/>
            </request>
        </entry>'''
    )
    

def run_transformation(input):
    body = input.get("BODY", {})

    bundle_id = str(uuid.uuid4())
    bundle=[f'<Bundle xmlns="http://hl7.org/fhir">\n\t<id value="{bundle_id}"/>\n\t<type value="transaction"/>']
    
    patient_id = hash_value(body.get("patientId", ""))
    birth_date = f'{body.get("birthdateYear")}-{body.get("birthdateMonth"), 1}'
    biologicalSex = body.get("biologicalSex")
    bundle.append(get_Patient(patient_id,birth_date,biologicalSex))

    primary_cancer = body.get("primaryCancer") or []
    primary = primary_cancer[0] if primary_cancer else {}

    diagnosis_date = f'{primary.get("cancerDiagnosisDateYear")}-{primary.get("cancerDiagnosisDateMonth")}'

    return '\n'.join(bundle)