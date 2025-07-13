import os
import json
import logging
import psycopg
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv(override=True)


def create_logger():
    log_dir = 'logs'
    file_name = 'call_api_log.log'
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, file_name),
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
    # Load token from pagination_state.json file
    token = load_token()

    # Parameter for querying
    params = {
        'q': 'data engineer seattle',
        'engine': 'google_jobs',
        'api_key': os.getenv('SERPAPI_API_KEY'),
        'output': 'json'
    }

    # if token is true/exists, parameter for next page token in API call is token
    if token:
        params['next_page_token'] = token

    search = GoogleSearch(params)
    results = search.get_dict()

    # Access the serpapi_pagination dict from nested json dict
    pagination = results.get('serpapi_pagination')

    # If a pagination dict exists, grab the next_page_token and save it to next_token variable
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
    else:
            return [], next_token



def connect_to_db():
    try:
        conn = psycopg.connect(
            host = os.getenv('DB_HOST'),
            dbname = "jobs_db",
            user = "postgres",
            password = os.getenv('DB_PASSWORD'),
            port = 5432,
            sslmode = "require",
            connect_timeout = 10
        )
        print("Connection Successful")
        return conn

    except Exception as e:
        print("Connection Failed")
        return None


def create_job_table(conn):
    # # Move this to main later!!!!
    # conn = connect_to_db()

    cursor = conn.cursor()

    create_jobs_table_query = """
    CREATE TABLE IF NOT EXISTS jobs (
        job_id VARCHAR(100) PRIMARY KEY NOT NULL,
        title VARCHAR(100),
        location VARCHAR(100),
        company_name VARCHAR(100),
        description VARCHAR(5000),
        qualifications VARCHAR(5000),
        benefits VARCHAR(500),
        responsibilities VARCHAR(5000),
        posted_at VARCHAR(100),
        schedule_type VARCHAR(100),
        dental_coverage VARCHAR(100),
        health_coverage VARCHAR(100)
    )
    """
    cursor.execute(create_jobs_table_query)
    conn.commit()
    cursor.close()
    
def insert_into_job_table(conn, all_jobs):

    cursor = conn.cursor()

    insert_query = """
    INSERT INTO 
    jobs ( job_id, title, location, company_name, description, qualifications, benefits, responsibilities, posted_at, schedule_type, dental_coverage,health_coverage)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    check_query = """ SELECT job_id FROM jobs WHERE job_id = %s"""

    skip_count = 0
    insert_count = 0
    for job in all_jobs:
        cursor.execute(check_query, (job.get('job_id'),))
        exists = cursor.fetchone()

        if exists:
            print("job already exists")
            skip_count += 1
            continue
        # Insert into table
        try:
            cursor.execute(insert_query, (
                job.get('job_id'),
                job.get('title'),
                job.get('location'),
                job.get('company_name'),
                job.get('description'),
                job.get('qualifications'),
                job.get('benefits'),
                job.get('responsibilities'),
                job.get('posted_at'),
                job.get('schedule_type'),
                job.get('dental_coverage'),
                job.get('health_coverage')
            ))
            insert_count += 1
            print(f"Inserted job_id {job['job_id']}")
            logging.info(f"Inserted job_if {job['job_id']}")
        
        except Exception as e:
            print(f"Error inserting job_id {job['job_id']}")
            logging.info(f"Error inserting job_id {job['job_id']}")
            conn.rollback()
            cursor = conn.cursor()

    conn.commit()
    cursor.close()

    print(f"Summary: {insert_count} inserted, {skip_count} skipped")
    logging.info(f"Summary: {insert_count} inserted, {skip_count} skipped")

def main():
    create_logger()
    logging.info('Starting Script to call Google APIs')

    all_jobs = []  # Store jobs from ALL pages
    page_count = 0

    while True:
        page_count += 1
        # Load token from pagination_state.json file
        current_token = load_token()
        logging.info(f"\n=== PAGE {page_count} ===")
        logging.info(f"Starting with token: {current_token}")

        # Get list of dicts and next_token variable from call_api function
        page_jobs, next_token = call_api()  # Get jobs from current page

        logging.info(f"Got {len(page_jobs) if page_jobs else 0} jobs")
        logging.info(f"Next token from API: {next_token}")

        if not page_jobs:  # No more jobs
            logging.info("No jobs found, breaking")
            break

        all_jobs.extend(page_jobs)  # Add this page's jobs to total
        logging.info(f"Total jobs so far: {len(all_jobs)}")

        # Check if we've reached the end
        if not next_token:  # No more pages - No more next tokens == blank/False
            logging.info("No next token, saving None and breaking")
            save_token(None) # Save nothing as toke bc none exists
            break
        else:
            logging.info(f"Saving token for next iteration: {next_token}")
            save_token(next_token) # Save this token for next iteration in pagination_state.jjson

    logging.info(f"Final total: {len(all_jobs)} jobs")
    # print(all_jobs[0])
    # return all_jobs

    conn = connect_to_db()
    if not conn:
        print("Failed to connect to db")
        logging.info("Failed to connect to db")
        return

    create_job_table(conn)
    insert_into_job_table(conn, all_jobs)
    conn.close()


if __name__ == "__main__":
    main()
