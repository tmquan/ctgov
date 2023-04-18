SELECT DISTINCT
    studies.nct_id,
    studies.brief_title,
    studies.official_title,
    detailed_descriptions.description,
    studies.study_type
FROM 
    ctgov.studies
JOIN ctgov.detailed_descriptions ON detailed_descriptions.nct_id = studies.nct_id 
;