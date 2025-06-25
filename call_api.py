import os
import json
import logging
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()


def create_logger():
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, 'call_api_log.log'),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_token():
    if os.path.exists('pagination_state.json'):
        with open('pagination_state.json', 'r') as f:
            return json.load(f).get('next_page_token')
    return None


def save_token(token):
    with open('pagination_state.json', 'w') as f:
        json.dump({'next_page_token': token}, f)


def call_api():
    token = load_token()
    params = {
        'q': 'data engineer seattle',
        'engine': 'google_jobs',
        'api_key': os.getenv('SERPAPI_API_KEY'),
        'output': 'json'
    }

    if token:
        params['next_page_token'] = token

    search = GoogleSearch(params)
    results = search.get_dict()

    
    pagination = results.get('serpapi_pagination')

    next_token = None
    if pagination:
        next_token = pagination.get('next_page_token')
    

    if 'jobs_results' in results:
        jobs = results['jobs_results']

        # Get just the first job
        if jobs:
            job_list = []  # Make sure the list isn't empty
            for job in jobs:
                # Extract Nested Dictionary Data
                job_data = {
                    'title': job.get('title', ''),
                    'location': job.get('location', ''),
                    'company_name': job.get('company_name', ''),
                    'description': job.get('description', ''),
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

                job_data['posted_at'] = extensions.get('posted_at', '')
                job_data['schedule_type'] = extensions.get('schedule_type', '')
                job_data['dental_coverage'] = extensions.get(
                    'dental_coverage', '')
                job_data['health_coverage'] = extensions.get(
                    'health_coverage', '')

                job_list.append(job_data)

        return job_list, next_token


def main():
    create_logger()
    logging.info('Starting Script to call Google APIs')

    all_jobs = []  # Store jobs from ALL pages
    page_count = 0

    while True:
        page_count += 1
        current_token = load_token()
        logging.info(f"\n=== PAGE {page_count} ===")
        logging.info(f"Starting with token: {current_token}")

        page_jobs, next_token = call_api()  # Get jobs from current page

        logging.info(f"Got {len(page_jobs) if page_jobs else 0} jobs")
        logging.info(f"Next token from API: {next_token}")

        if not page_jobs:  # No more jobs
            logging.info("No jobs found, breaking")
            break

        all_jobs.extend(page_jobs)  # Add this page's jobs to total
        logging.info(f"Total jobs so far: {len(all_jobs)}")

        # Check if we've reached the end
        if not next_token:  # No more pages
            logging.info("No next token, saving None and breaking")
            save_token(None)
            break
        else:
            logging.info(f"Saving token for next iteration: {next_token}")
            save_token(next_token)

    logging.info(f"Final total: {len(all_jobs)} jobs")
    print(all_jobs[0])
    return all_jobs



if __name__ == "__main__":
    main()
