-- 

SELECT 
    studies.nct_id, 
    studies.official_title,
    studies.study_type
FROM 
    ctgov.studies
;
-- 

--
select    
    studies.nct_id,    
    --    
    -- Descriptive Information    
    --    
    studies.brief_title, -- Brief Title    
    studies.official_title, -- Offical Title    
    bstudies.description as brief_description, -- Brief Summary    
    dd.description as detailed_description,    
    studies.study_type, -- Study type    
    e.population,    
    bc.mesh_term as condition_mesh,    
    bi.mesh_term as intervention_mesh,    
    k.keywords,    
    --    
    -- Recruitment Information    
    --    
    studies.overall_status, 
    -- Recruiting Status    
    e.criteria, -- Ecligibility Criteria    
    e.gender, -- Sex/Gender    
    e.minimum_age, -- Age Limits    
    e.maximum_age, -- Age Limits    
    e.healthy_volunteers, -- Accept healthy volunteers    
    l.locations, -- Location Countries    
    --    
    -- Study Design    
    --    
    studies.phase, -- Study Phase    
    --    
    -- Administrative Information    
    --    
    sp.sponsors, -- Sponsors    
    oo.officials -- Officials
from    
    ctgov.studies s
    join ctgov.eligibilities e on studies.nct_id = e.nct_id 
    join (        
        select nct_id, string_agg(mesh_term, ', ') as mesh_term from ctgov.browse_conditions group by nct_id
    ) bc on studies.nct_id = bc.nct_id
    join (        
        select nct_id, string_agg(mesh_term, ', ') as mesh_term from ctgov.browse_interventions group by nct_id
    ) bi on studies.nct_id = bi.nct_id
    join ctgov.brief_summaries bs on studies.nct_id = bstudies.nct_id
    join ctgov.detailed_descriptions dd on studies.nct_id = dd.nct_id 
    join (        
        select nct_id, string_agg(name, ', ') as keywords from ctgov.keywords group by nct_id 
    ) k on studies.nct_id = k.nct_id
    join (        
        select nct_id, json_agg(json_build_object('name', "name", 'city', city, 'state', state, 'country', country)) as locations from facilities group by nct_id
    ) l on studies.nct_id = l.nct_id
    join (        
        select nct_id, json_agg(json_build_object('id', "id", 'agency_class', agency_class, 'lead_or_collaborator', lead_or_collaborator, 'name', "name")) as sponsors from sponsors group by nct_id
    ) sp on studies.nct_id = sp.nct_id
    join(        
        select nct_id, json_agg(json_build_object('id', "id", 'role', "role", 'name', "name", 'affiliation', affiliation)) as officials from overall_officials group by nct_id
    ) oo on studies.nct_id = oo.nct_id
;
--

SELECT DISTINCT
    studies.study_type, 
    studies.official_title,
    studies.nct_id
FROM 
    ctgov.studies
;
-- 
SELECT 
DISTINCT studies.nct_id, 
    studies.official_title,
    facilities.name, 
    facilities.city, 
    facilities.state, 
    facilities.zip, 
    facilities.country, 
    studies.study_type
FROM 
    ctgov.studies
JOIN ctgov.facilities ON facilities.nct_id = studies.nct_id 
;
-- 

-- 
SELECT 
DISTINCT studies.nct_id, 
    studies.official_title,
    eligibilities.criteria, 
    facilities.name, 
    facilities.city, 
    facilities.state, 
    facilities.zip, 
    facilities.country, 
    studies.study_type
FROM 
    ctgov.studies
JOIN ctgov.facilities ON facilities.nct_id = studies.nct_id 
JOIN ctgov.eligibilities ON eligibilities.nct_id = studies.nct_id 
;
-- 

SELECT DISTINCT
    studies.nct_id, 
	detailed_descriptions.description,
    eligibilities.criteria, 
    facilities.name, 
    facilities.city, 
    facilities.state, 
    facilities.zip, 
    facilities.country, 
    participant_flows.recruitment_details, 
    participant_flows.pre_assignment_details, 
    studies.study_type, 
    studies.brief_title, 
    studies.official_title
FROM 
    ctgov.studies
    JOIN ctgov.baseline_measurements ON baseline_measurements.nct_id = studies.nct_id 
    JOIN ctgov.brief_summaries ON brief_summaries.nct_id = studies.nct_id 
    JOIN ctgov.design_groups ON design_groups.nct_id = studies.nct_id 
    JOIN ctgov.design_outcomes ON design_outcomes.nct_id = studies.nct_id 
    JOIN ctgov.detailed_descriptions ON detailed_descriptions.nct_id = studies.nct_id 
    JOIN ctgov.eligibilities ON eligibilities.nct_id = studies.nct_id 
    JOIN ctgov.facilities ON facilities.nct_id = studies.nct_id 
    JOIN ctgov.participant_flows ON participant_flows.nct_id = studies.nct_id
