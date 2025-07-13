import os
import logging
import psycopg
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def call_api_one_job():
    params = {
        'q': 'data engineer seattle',
        'engine': 'google_jobs',
        'api_key': os.getenv('SERPAPI_API_KEY'),
        'output': 'json'
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if 'jobs_results' in results and results['jobs_results']:
        job = results['jobs_results'][0]

        job_data = {
            'job_id': job.get('job_id', ''),
            'title': job.get('title', ''),
            'location': job.get('location', ''),
            'company_name': job.get('company_name', ''),
            'description': job.get('description', ''),
            'qualifications': '',
            'benefits': '',
            'responsibilities': '',
            'posted_at': '',
            'schedule_type': '',
            'dental_coverage': '',
            'health_coverage': ''
        }

        job_highlights = job.get('job_highlights', [])
        for highlight in job_highlights:
            title = highlight.get('title', '').lower()
            items = highlight.get('items', [])
            if 'qualification' in title:
                job_data['qualifications'] = ', '.join(items)
            elif 'benefits' in title:
                job_data['benefits'] = ', '.join(items)
            elif 'responsibilities' in title:
                job_data['responsibilities'] = ', '.join(items)

        extensions = job.get('detected_extensions', {})
        job_data['posted_at'] = extensions.get('posted_at', '')
        job_data['schedule_type'] = extensions.get('schedule_type', '')
        job_data['dental_coverage'] = extensions.get('dental_coverage', '')
        job_data['health_coverage'] = extensions.get('health_coverage', '')

        return job_data
    else:
        logging.warning("No jobs found in API response")
        return None


def connect_to_db():
    try:
        conn = psycopg.connect(
            host=os.getenv('DB_HOST'),
            dbname=os.getenv('DB_NAME', 'jobs_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT', 5432)),
            sslmode="require",
            connect_timeout=10
        )
        logging.info("Database connection successful")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None


def delete_job_table(conn):
    delete_jobs_table = """
    DROP TABLE if EXISTS jobs;
    """
    with conn.cursor() as cursor:
        cursor.execute(delete_jobs_table)
    conn.commit()
    logging.info("Jobs table ensured to exist")


def create_job_table(conn):
    create_jobs_table_query = """
    CREATE TABLE IF NOT EXISTS jobs (
        job_id VARCHAR(1000) PRIMARY KEY NOT NULL,
        title VARCHAR(1000),
        location VARCHAR(1000),
        company_name VARCHAR(1000),
        description TEXT,
        qualifications TEXT,
        benefits TEXT,
        responsibilities TEXT,
        posted_at VARCHAR(1000),
        schedule_type VARCHAR(1000),
        dental_coverage VARCHAR(1000),
        health_coverage VARCHAR(1000)
    )
    """
    with conn.cursor() as cursor:
        cursor.execute(create_jobs_table_query)
    conn.commit()
    logging.info("Jobs table ensured to exist")


def insert_job(conn, job):
    check_query = "SELECT job_id FROM jobs WHERE job_id = %s"
    insert_query = """
    INSERT INTO jobs
    (job_id, title, location, company_name, description, qualifications, benefits, responsibilities,
     posted_at, schedule_type, dental_coverage, health_coverage)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    with conn.cursor() as cursor:
        cursor.execute(check_query, (job['job_id'],))
        if cursor.fetchone():
            logging.info(f"Job {job['job_id']} already exists, skipping insert")
            return False
        cursor.execute(insert_query, (
            job['job_id'], job['title'], job['location'], job['company_name'], job['description'],
            job['qualifications'], job['benefits'], job['responsibilities'], job['posted_at'],
            job['schedule_type'], job['dental_coverage'], job['health_coverage']
        ),)
    conn.commit()
    logging.info(f"Inserted job {job['job_id']}")
    return True


def main():
    job = call_api_one_job()
    if not job:
        logging.error("No job data fetched; exiting")
        return

    conn = connect_to_db()
    if not conn:
        logging.error("Could not connect to DB; exiting")
        return
    delete_job_table(conn)
    create_job_table(conn)
    inserted = insert_job(conn, job)
    if inserted:
        logging.info("Job inserted successfully")
    else:
        logging.info("Job was already in DB")

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM jobs LIMIT 5;")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            
    conn.close()


if __name__ == "__main__":
    main()