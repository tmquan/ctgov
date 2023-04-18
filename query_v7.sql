SELECT
    studies.nct_id,
    MAX(studies.brief_title) AS brief_title,
    MAX(studies.official_title) AS official_title,
    STRING_AGG(DISTINCT baseline_measurements.description, ' ') AS baseline_measurements,
    STRING_AGG(DISTINCT brief_summaries.description, ' ') AS brief_summaries,
    STRING_AGG(DISTINCT detailed_descriptions.description, ' ') AS detailed_descriptions,
    MAX(eligibilities.criteria) AS criteria, 
    MAX(facilities.name) AS facilities, 
    MAX(facilities.city) AS city, 
    MAX(facilities.state) AS state, 
    MAX(facilities.zip) AS zip, 
    MAX(facilities.country) AS country, 
    MAX(participant_flows.recruitment_details) AS recruitment_details, 
    MAX(participant_flows.pre_assignment_details) AS pre_assignment_details, 
    MAX(studies.study_type) AS study_type
FROM 
    ctgov.studies
INNER JOIN ctgov.baseline_measurements ON baseline_measurements.nct_id = studies.nct_id 
INNER JOIN ctgov.brief_summaries ON brief_summaries.nct_id = studies.nct_id 
INNER JOIN ctgov.detailed_descriptions ON detailed_descriptions.nct_id = studies.nct_id 
INNER JOIN ctgov.eligibilities ON eligibilities.nct_id = studies.nct_id 
INNER JOIN ctgov.facilities ON facilities.nct_id = studies.nct_id 
INNER JOIN ctgov.participant_flows ON participant_flows.nct_id = studies.nct_id 
GROUP BY studies.nct_id;
