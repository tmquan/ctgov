SELECT DISTINCT
    studies.nct_id,
    studies.brief_title,
    studies.official_title,
    studies.study_type
FROM 
    ctgov.studies
;