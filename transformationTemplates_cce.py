import logging
log = logging.getLogger(__name__)

def get_Patient(patient_id,patient_identifier,birth_date,biologicalSex):
    return (f'''
        <entry>
            <fullUrl value="CCE/Patient/{patient_id}"/>
            <resource>
                <Patient>
                    <id value="{patient_id}"/>
                    <meta>
                        <profile value="https://simplifier.net/CCE/StructureDefinition-CCE-Patient"/>
                    </meta>
                    <identifier>
                        <value value="{patient_identifier}"/>
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

def get_Observation_Vitalstatus(obs_id,patient_id,vitalstatus_value,vitalstatus_date):
    effective = ""
    if vitalstatus_date:
        effective = f'\n                    <effectiveDateTime value="{vitalstatus_date}"/>'
    conditional_update=""
    if vitalstatus_value=="alive":
        conditional_update='\n                <ifNoneMatch value="*"/>'
    return (f'''
        <entry>
            <fullUrl value="CCE/Observation/{obs_id}"/>
            <resource>
                <Observation>
                    <id value="{obs_id}"/>
                    <status value="final" />
                    <code>
                        <coding>
                            <system value="http://loinc.org"/>
                            <code value="75186-7"/>
                        </coding>
                    </code>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>{effective}
                    <valueCodeableConcept>
                        <coding>
                            <system value="https://www.cancercoreeurope.eu/fhir/core/CodeSystem/VitalStatusCS"/>
                            <code value="{vitalstatus_value}"/>
                        </coding>
                    </valueCodeableConcept>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>{conditional_update}
                <url value="Observation/{obs_id}"/>
            </request>
        </entry>'''
    )

def get_Condition(condition_id,diagnosis_icd10,diagnosis_icdo3,patient_id,diagnosis_date,diagnosis_icdo3_text, laterality):
    log.debug(f'get_Condition with parameters: condition_id={condition_id},diagnosis_icd10={diagnosis_icd10},diagnosis_icdo3={diagnosis_icdo3},patient_id={patient_id},diagnosis_date={diagnosis_date},diagnosis_icdo3_text={diagnosis_icdo3_text}, laterality={laterality}')
    sitelocation = ""
    if laterality:
        sitelocation=f'''
                        <coding>
                            <system value="https://www.cancercoreeurope.eu/fhir/core/CodeSystem/SitelocationCS" />
                            <code value="{laterality}" />
                        </coding>'''
    diagnosis_text = ""
    if diagnosis_icdo3_text:
        diagnosis_text=f'''
                        <text value="{diagnosis_icdo3_text}" />'''
    bodysite = ""
    if diagnosis_icdo3:
        bodysite=f'''
                    <bodySite>
                        <coding>
                            <system value="urn:oid:2.16.840.1.113883.6.43.1"/>
                            <code value="{diagnosis_icdo3}"/>
                        </coding>{diagnosis_text}{sitelocation}
                    </bodySite>'''
    return (f'''
        <entry>
            <fullUrl value="CCE/Condition/{condition_id}"/>
            <resource>
                <Condition>
                    <id value="{condition_id}"/>
                    <code>
                        <coding>
                            <system value="http://fhir.de/CodeSystem/bfarm/icd-10-gm"/>
                            <code value="{diagnosis_icd10}"/>
                        </coding>
                    </code>{bodysite}
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <onsetDateTime value="{diagnosis_date}"/>
                </Condition>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Condition/{condition_id}"/>
            </request>
        </entry>'''
    )

def get_Observation_Histology(obs_id,patient_id,condition_id,histology_date,histology_value):
    date = date_helper(histology_date)
    return (f'''
        <entry>
            <fullUrl value="CCE/Observation/{obs_id}-histology"/>
            <resource>
                <Observation>
                    <id value="{obs_id}-histology"/>
                    <status value="final"/>
                    <code>
                        <coding>
                            <system value="http://loinc.org"/>
                            <code value="59847-4"/>
                        </coding>
                    </code>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <focus>
                        <reference value="Condition/{condition_id}" />
                    </focus>{date}
                    <valueCodeableConcept>
                        <coding>
                            <system value="urn:oid:2.16.840.1.113883.6.43.1"/>
                            <code value="{histology_value}"/>
                        </coding>
                    </valueCodeableConcept>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Observation/{obs_id}-histology"/>
            </request>
        </entry>''')

def get_Observation_UICC(obs_id,patient_id,condition_id,uicc_stage,tnm_prefix,tnm_t,tnm_n,tnm_m):
    log.debug(f'get_Observation_UICC with parameters: obs_id={obs_id},patient_id={patient_id},condition_id={condition_id},uicc_stage={uicc_stage},tnm_prefix={tnm_prefix},tnm_t={tnm_t},tnm_n={tnm_n},tnm_m={tnm_m}')
    date = ""#date_helper(tnm_date)
    uicc = ""
    if uicc_stage:
        uicc = f'''
                    <valueCodeableConcept>
                        <coding>
                            <system value="https://www.cancercoreeurope.eu/fhir/core/CodeSystem/UICCStageCS"/>
                            <code value="{uicc_stage}"/>
                        </coding>
                    </valueCodeableConcept>'''
    prefix = ""
    if tnm_prefix:
        prefix = f'''
                        <extension url="http://CCE.org/fhir/StructureDefinition/CCE-Extension-TNMcpuPrefix">
                            <valueCodeableConcept>
                                <coding>
                                    <code value="{tnm_prefix}" />
                                </coding>
                            </valueCodeableConcept>
                        </extension>'''
    t=tnm_helper(tnm_t, prefix, "21905-5", "t")
    n=tnm_helper(tnm_n, prefix, "201906-3", "n")
    m=tnm_helper(tnm_m, prefix, "21907-1", "m")
    return (f'''
        <entry>
            <fullUrl value="CCE/Observation/{obs_id}"/>
            <resource>
                <Observation>
                    <id value="{obs_id}"/>
                    <status value="final" />
                    <code>
                        <coding>
                            <system value="http://loinc.org"/>
                            <code value="21908-9"/>
                        </coding>
                    </code>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <focus>
                        <reference value="Condition/{condition_id}"/>
                    </focus>{date}{uicc}{t}{n}{m}
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Observation/{obs_id}"/>
            </request>
        </entry>'''
    )

def get_Observation_Lab_Marker(obs_id,patient_id,specimen_id,biomarker,biomarker_status,gene_name):
    return (f'''
        <entry>
            <fullUrl value="CCE/Observation/{obs_id}-lab"/>
            <resource>
                <Observation>
                    <id value="{obs_id}-lab"/>
                    <code>
                        <coding>
                            <system value="http://terminology.hl7.org/CodeSystem/observation-category"/>
                            <code value="laboratory"/>
                        </coding>
                    </code>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <effectiveDateTime value="{date}"/>
                    <specimen>
                        <reference value="{specimen_id}"/>
                    </specimen>
                    <valueQuantity>TODO
                        <value value="{unit_value}"/>
                        <system value="http://unitsofmeasure.org"/>
                        <code value="{unit}"/>
                    </valueQuantity>
                    <component>
                        TODO
                    </component>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Observation/{obs_id}-lab"/>
            </request>
        </entry>'''
    )

def get_Observation_Gene_Marker(obs_id,patient_id,specimen_id,mutation_type,gene_name):
    return (f'''
        <entry>
            <fullUrl value="CCE/Observation/{obs_id}-gen"/>
            <resource>
                <Observation>
                    <id value="{obs_id}-gen"/>
                    <code>
                        <coding>
                            <system value="http://loinc.org"/>
                            <code value="69548-6"/>
                        </coding>
                    </code>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <specimen>
                        <reference value="{specimen_id}"/>
                    </specimen>
                    <valueCodeableConcept>
                        <coding>
                            <system value="http://CCE.dkfz.de/fhir/CCE/CodeSystem/MutationTypeCS"/>
                            <code value="{mutation_type}"/>
                        </coding>
                    </valueCodeableConcept>
                    <component>
                        <code>
                            <coding>
                                <system value="http://loinc.org"/>
                                <code value="48018-6"/>
                            </coding>
                        </code>
                        <valueCodeableConcept>
                            <coding>
                                <system value="http://www.genenames.org"/>
                                <code value="{gene_name}"/>
                            </coding>
                        </valueCodeableConcept>
                    </component>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Observation/{obs_id}-gen"/>
            </request>
        </entry>'''
    )

def get_MedicationStatement(med_id,patient_id,condition_id,atc_code,atc_text,med_therapy,med_date,med_date_end):
    log.debug(f'get_MedicationStatement with parameters: med_id={med_id},patient_id={patient_id},condition_id={condition_id},atc_code={atc_code},atc_text={atc_text},med_therapy={med_therapy},med_date={med_date},med_date_end={med_date_end}')
    period = period_helper(med_date, med_date_end, "MedicationStatement")
    condition = ""
    if condition_id:
        condition = f'''
                    <reasonReference>
                        <reference value="Condition/{condition_id}"/>
                    </reasonReference>'''
    atcText=""
    if atc_text:
        atcText = f'''<text value="{atc_text}"/>'''
    atc=""
    if atc_code:
        atc= f'''
                    <medicationCodeableConcept>
                        <coding>
                            <system value="http://fhir.de/CodeSystem/bfarm/atc"/>
                            <code value="{atc_code}"/>
                        </coding>{atcText}
                    </medicationCodeableConcept>'''
    return (f'''
        <entry>
            <fullUrl value="CCE/MedicationStatement/{med_id}"/>
            <resource>
                <MedicationStatement>
                    <id value="{med_id}"/>
                    <category>
                        <coding>
                            <system value="https://www.cancercoreeurope.eu/fhir/core/CodeSystem/SYSTTherapyTypeCS"/>
                            <code value="{med_therapy}"/>
                        </coding>
                    </category>{atc}
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>{period}{condition}
                </MedicationStatement>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="MedicationStatement/{med_id}"/>
            </request>
        </entry>'''
    )

def get_Procedure(prod_type,prod_id,patient_id,condition_id,prod_start,prod_end):
    log.debug(f'get_Procedure with parameters: prod_type={prod_type},prod_id={prod_id},patient_id={patient_id},condition_id={condition_id},prod_start={prod_start},prod_end={prod_end}')
    if prod_type not in {"OP", "RT"}:
        raise ValueError(f'Procedure type "{prod_type}" must be OP or RT')
    period = period_helper(prod_start, prod_end, "Procedure")
    return (f'''
        <entry>
            <fullUrl value="https://www.cancercoreeurope.eu/fhir-xml/examples/{prod_id}"/>
            <resource>
                <Procedure>
                    <id value="{prod_id}" />
                    <category>
                        <coding>
                            <system value="https://www.cancercoreeurope.eu/fhir/core/CodeSystem/SYSTTherapyTypeCS" />
                            <code value="{prod_type}" />
                        </coding>
                    </category>
                    <subject>
                        <reference value="Patient/{patient_id}" />
                    </subject>{period}
                    <reasonReference>
                        <reference value="Condition/{condition_id}" />
                    </reasonReference>
                </Procedure>
            </resource>
            <request>
                <method value="PUT" />
                <url value="Procedure/{prod_id}" />
            </request>
        </entry>'''
    )

def get_Observation_Satellite(satellite_id,patient_id,specimen_date,specimen_id,satellite_value):
    return (f'''
        <entry>
            <fullUrl value="CCE/Observation/{satellite_id}"/>
            <resource>
                <Observation>
                    <id value="{satellite_id}"/>
                    <code>
                        <coding>
                            <system value="http://loinc.org"/>
                            <code value="81695-9"/>
                            <display value="Microsatellite instability [Interpretation] in Cancer specimen Qualitative"/>
                        </coding>
                    </code>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <effectiveDateTime value="{specimen_date}"/>
                    <specimen>
                        <reference value="{specimen_id}"/>
                    </specimen>
                    <valueCodeableConcept>
                        <coding>
                            <system value="MicrosatelliteInstabilityStage"/>
                            <code value="{satellite_value}"/>
                        </coding>
                    </valueCodeableConcept>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Observation/{satellite_id}"/>
            </request>
        </entry>'''
    )

def get_Specimen(specimen_id,patient_id,specimen_type,specimen_date):
    date = ""
    if specimen_date:
        date = f'''
                    <collection>
                        <collectedDateTime value="{specimen_date}"/>
                    </collection>'''
    return (f'''
        <entry>
            <fullUrl value="CCE/Specimen/{specimen_id}"/>
            <resource>
                <Specimen>
                    <id value="{specimen_id}"/>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <type>
                        <coding>
                            <system value="https://www.cancercoreeurope.eu/fhir/core/CodeSystem/SampleMaterialType"/>
                            <code value="{specimen_type}"/>
                        </coding>
                    </type>{date}
                </Specimen>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Specimen/{specimen_id}"/>
            </request>
        </entry>'''
    )


#########helper
def date_helper(date_in):
    date=""
    if date_in:
        date=f'''
                    <effectiveDateTime value="{date_in}"/>'''
    return date

def period_helper(start_in, end_in, resource_type):
    if not (start_in or end_in):
        return ""
    tag = {"MedicationStatement": "effectivePeriod", "Procedure": "performedPeriod"}.get(resource_type)
    if not tag:
        raise ValueError(f"unsupported resource_type: {resource_type}")
    start = f'''
                        <start value="{start_in}"/>''' if start_in else ""
    end = f'''
                        <end value="{end_in}"/>''' if end_in else ""
    return f'''
                    <{tag}>{start}{end}
                    </{tag}>'''

def tnm_helper(tnm_in, prefix, loinc, tnmLetter):
    tnm=""
    if tnm_in:
        tnm=f'''
                    <component>{prefix}
                        <code>
                            <coding>
                                <system value="http://loinc.org" />
                                <code value="{loinc}" />
                            </coding>
                        </code>
                        <valueCodeableConcept>
                            <coding>
                                <system value="http://CCE.org/fhir/CodeSystem/TNM{tnmLetter.upper()}CS" />
                                <code value="{tnm_in}" />
                            </coding>
                        </valueCodeableConcept>
                    </component>'''
    return tnm