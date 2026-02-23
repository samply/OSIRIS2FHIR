def get_Patient(patient_id,patient_identifier,birth_date,biologicalSex):
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
    effective=""
    if vitalstatus_date:
        effective = f'\n                    <effectiveDateTime value="{vitalstatus_date}"/>'
    conditional_update=""
    if vitalstatus_value=="alive":
        conditional_update='\n        <ifNoneMatch value="*"/>'
    return (f'''
        <entry>
            <fullUrl value="PSCC/Observation/{obs_id}-vital"/>
            <resource>
                <Observation>
                    <id value="{obs_id}-vital"/>
                    <meta>
                        <profile value="https://simplifier.net/PSCC-Test/StructureDefinition-PSCC-VitalStatus"/>
                    </meta>
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
                            <system value="https://simplifier.net/PSCC/ValueSet/Vitalstatus"/>
                            <code value="{vitalstatus_value}"/>
                        </coding>
                    </valueCodeableConcept>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>{conditional_update}
                <url value="Observation/{obs_id}-vital"/>
            </request>
        </entry>'''
    )

def get_Condition(condition_id,diagnosis_icd10,diagnosis_icdo3,patient_id,diagnosis_date):
    return (f'''
        <entry>
            <fullUrl value="PSCC/Condition/{condition_id}"/>
            <resource>
                <Condition>
                    <id value="{condition_id}"/>
                    <meta>
                        <profile value="https://simplifier.net/pscc/primarydiagnosis"/>
                    </meta>
                    <code>
                        <coding>
                            <system value="http://hl7.org/fhir/sid/icd-10"/>
                            <code value="{diagnosis_icd10}"/>
                        </coding>
                    </code>
                    <bodySite>
                        <coding>
                            <system value="http://hl7.org/fhir/sid/icd-O3-topography"/>
                            <code value="{diagnosis_icdo3}"/>
                        </coding>
                    </bodySite>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <onsetDateTime>
                        <value value="{diagnosis_date}"/>
                        '''#<unit value="Jahre"/>
                        #<system value="http://unitsofmeasure.org/"/>
                    +f'''</onsetDateTime>
                </Condition>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Condition/{condition_id}"/>
            </request>
        </entry>'''
    )
        
def get_Observation_UICC(obs_id,patient_id,condition_id,tnm_date,uicc_stage):
    return (f'''
        <entry>
            <fullUrl value="PSCC/Observation/{obs_id}-tnm"/>
            <resource>
                <Observation>
                    <id value="{obs_id}-tnm"/>
                    <meta>
                        <profile value="https://simplifier.net/PSCC/TNMStage"/>
                    </meta>
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
                    </focus>
                    <effectiveDateTime value="{tnm_date}"/>
                    <valueCodeableConcept>
                        <coding>
                            <system value="https://simplifier.net/PSCC/tnmstagevs"/>
                            <code value="{uicc_stage}"/>
                        </coding>
                    </valueCodeableConcept>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Observation/{obs_id}-tnm"/>
            </request>
        </entry>'''
    )

def get_Observation_Histology(obs_id,patient_id,histology_date,histology_value,specimen_id):
    return (f'''
        <entry>
            <fullUrl value="PSCC/Observation/{obs_id}-histology"/>
            <resource>
                <Observation>
                    <id value="{obs_id}-histology"/>
                    <meta>
                        <profile value="TODO"/>
                    </meta>
                    <code>
                        <coding>
                            <system value="http://loinc.org"/>
                            <code value="59847-4"/>
                        </coding>
                    </code>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <effectiveDateTime value="{histology_date}"/>
                    <valueCodeableConcept>
                        <coding>
                            <system value="urn:oid:2.16.840.1.113883.6.43.1"/>
                            <code value="{histology_value}"/>
                        </coding>
                    </valueCodeableConcept>
                    <specimen>
                        <reference value="{specimen_id}"/>
                    </specimen>
                </Observation>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Observation/{obs_id}-histology"/>
            </request>
        </entry>''')


def get_Observation_Gene(obs_id,patient_id,specimen_id,mutation_type,gene_name):
    return (f'''
        <entry>
            <fullUrl value="PSCC/Observation/{obs_id}-gen"/>
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
                            <system value="http://itcc.dkfz.de/fhir/itcc/CodeSystem/MutationTypeCS"/>
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

def get_MedicationStatement(med_id,med_therapy,patient_id,med_date,med_date_end):
    return (f'''
        <entry>
            <fullUrl value="PSCC/MedicationStatement/{med_id}"/>
            <resource>
                <MedicationStatement>
                    <id value="{med_id}"/>
                    <meta>
                        <profile value="TODO"/>
                    </meta>
                    <category>
                        <coding>
                            <system value="http://pscc.org/fhir/TODO"/>
                            <code value="{med_therapy}"/>
                        </coding>
                    </category>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <effectivePeriod>
                        <start value="{med_date}"/>
                        <end value="{med_date_end}"/>
                    </effectivePeriod>
                </MedicationStatement>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="MedicationStatement/{med_id}"/>
            </request>
        </entry>'''
    )

def get_Observation_Satellite(satellite_id,patient_id,specimen_date,specimen_id,satellite_value):
    return (f'''
        <entry>
            <fullUrl value="PSCC/Observation/{satellite_id}"/>
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
    return (f'''
        <entry>
            <fullUrl value="PSCC/Specimen/{specimen_id}"/>
            <resource>
                <Specimen>
                    <id value="{specimen_id}"/>
                    <meta>
                        <profile value="TODO-simplifier"/>
                    </meta>
                    <subject>
                        <reference value="Patient/{patient_id}"/>
                    </subject>
                    <type>
                        <coding>
                            <system value="https://pscc.org/fhir/CodeSystem/SampleMaterialType"/>
                            <code value="{specimen_type}"/>
                        </coding>
                    </type>
                    <collection>
                        <collectedDateTime value="{specimen_date}"/>
                    </collection>
                </Specimen>
            </resource>
            <request>
                <method value="PUT"/>
                <url value="Specimen/{specimen_id}"/>
            </request>
        </entry>'''
    )