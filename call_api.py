import os
import json
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

params = {
    'q' : 'data engineer seattle',
    'engine': 'google_jobs',
    'api_key' : os.getenv('SERPAPI_API_KEY'),
    'output': 'json',

}

search = GoogleSearch(params)
results = search.get_dict()


if 'jobs_results' in results:
    jobs = results['jobs_results']
    
    # Get just the first job
    if jobs:
        job_list = []  # Make sure the list isn't empty
        for job in jobs:
            # Extract Nested Dictionary Data

            
            # print(json.dumps(jobs[0], indent=2))

            job_data = {
                'title': job.get('title',''),
                'location': job.get('location',''),
                'company_name': job.get('company_name',''),
                'description': job.get('description',''),
                'job_id': job.get('job_id', '')
                }
            
            # Extract Job highlights info out of job_highlights list of dictionaries.
            job_highlights = job.get('job_highlights', [])

            for highlight in job_highlights:
                title = highlight.get('title', "").lower()
                item = highlight.get('items', [])

                if "qualification" in title:
                    job_data['qualifications'] = ','.join(item)
                elif 'benefits' in title:
                    job_data['benefits'] = ','.join(item)
                elif 'responsibilities' in title:
                    job_data['responsibilities'] = ','.join(item)


            # Extract extension data form extensions dictionary
            extensions = job.get('detected_extensions', {})
            
        
            
            job_data['posted_at'] = extensions.get('posted_at','')
            job_data['schedule_type'] = extensions.get('schedule_type', '')
            job_data['dental_coverage'] = extensions.get('dental_coverage', '')
            job_data['health_coverage'] = extensions.get('health_coverage', '')

            job_list.append(job_data)

    print(json.dumps(job_list, indent=2))



# title
# location
# company_name
# extensions
# description
# job_highlights
#  - title: qualifications, items
#  - title: responsibilities, items
# job_id
