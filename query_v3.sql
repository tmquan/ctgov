SELECT DISTINCT
    studies.nct_id,
    studies.brief_title,
    studies.official_title,
    brief_summaries.description,
    detailed_descriptions.description,
    eligibilities.criteria, 
    studies.study_type
FROM 
    ctgov.studies
JOIN ctgov.brief_summaries ON brief_summaries.nct_id = studies.nct_id 
JOIN ctgov.detailed_descriptions ON detailed_descriptions.nct_id = studies.nct_id 
JOIN ctgov.eligibilities ON eligibilities.nct_id = studies.nct_id 
;