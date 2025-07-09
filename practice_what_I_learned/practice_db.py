import psycopg
import os

job_list= []

def connect_to_db():
    try:
        conn = psycopg.connect(
            host = os.getenv('DB_HOST'),
            dbname = "mydb",
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


def create_jobs_table(conn):
    conn = connect_to_db()

    cursor = conn.cursor()

    create_job_query = """
        CREATE TABLE jobs AS(
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
        health_coverage VARCHAR(100))
        """

    cursor.execute(create_job_query)
    conn.commit()
    conn.close()

def insert_into_jobs(conn):
    conn = connect_to_db()

    cursor = conn.cursor()

    insert_query = """
    INSERT INTO 
    jobs(job_id, title, location, company_name, description, qualifications, benefits, responsibilities, posted_at, schedule_type, dental_coverage, health_coverage)
    values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    check_query = "SELECT * FROM jobs WHERE job_id = %s"

    for job in job_list:
        cursor.execute(check_query, job.get('job_id'),)
        duplicate = cursor.fectone()
        
        skip_jobs = 0
        inserted_jobs = 0
        if duplicate:
            skip_jobs += 1
            pass 
        else:
            cursor.execute(insert_query, 
                           (job.get('job_id'),
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
                            job.get('health_coverage')),
            )
            inserted_jobs += 1

    print(f'skipped jobs = {skip_jobs}')
    print(f'inserted_jobs = {inserted_jobs}')

    cursor.commit()
    cursor.close()

    
