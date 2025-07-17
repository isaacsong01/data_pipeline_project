
SELECT Distinct *
FROM {{source('raw', 'jobs')}}
WHERE job_id IS NOT NULL
