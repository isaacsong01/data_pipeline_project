Data Pipeline Project
====================

DESCRIPTION
-----------
A Python-based data pipeline that fetches job listings from Google Jobs API via SerpAPI and stores them in a PostgreSQL database. The pipeline handles pagination to collect comprehensive job data and includes duplicate checking to prevent data redundancy.

FEATURES
--------
- Fetches job listings for "data engineer seattle" from Google Jobs API
- Handles API pagination to collect all available results
- Stores job data in PostgreSQL database with duplicate prevention
- Comprehensive logging system for monitoring pipeline operations
- Extracts detailed job information including qualifications, benefits, and responsibilities

REQUIREMENTS
------------
- Python 3.13+
- PostgreSQL database
- SerpAPI account and API key
- Environment variables for database and API configuration

DEPENDENCIES
------------
- psycopg[binary] >= 3.2.9 (PostgreSQL adapter)
- google-search-results >= 2.4.2 (SerpAPI client)
- python-dotenv >= 0.9.9 (environment variables)
- pandas >= 2.3.0 (data manipulation)
- requests >= 2.32.4 (HTTP requests)

SETUP
-----
1. Install dependencies:
   uv sync

2. Create a .env file with:
   SERPAPI_API_KEY=your_serpapi_key_here
   DB_HOST=your_database_host
   DB_PASSWORD=your_database_password

3. Ensure PostgreSQL database "mydb" exists and is accessible

USAGE
-----
Run the main pipeline:
python call_api.py

The script will:
- Create necessary log directory and table structure
- Fetch job listings with pagination support
- Store results in PostgreSQL database
- Log all operations to logs/call_api_log.log

DATABASE SCHEMA
---------------
Jobs table contains:
- job_id (VARCHAR(100), PRIMARY KEY)
- title (VARCHAR(100))
- location (VARCHAR(100))
- company_name (VARCHAR(100))
- description (VARCHAR(5000))
- qualifications (VARCHAR(5000))
- benefits (VARCHAR(500))
- responsibilities (VARCHAR(5000))
- posted_at (VARCHAR(100))
- schedule_type (VARCHAR(100))
- dental_coverage (VARCHAR(100))
- health_coverage (VARCHAR(100))

FILES
-----
- call_api.py: Main pipeline script
- db_connect.py: Database connection test utility
- practice.py: Development/testing script
- practice_call_api.py: Alternative API testing script
- reference.py: Reference implementation
- pyproject.toml: Project configuration and dependencies
- logs/: Directory for log files

LOGGING
-------
All operations are logged to logs/call_api_log.log with timestamps and detailed information about:
- API calls and pagination
- Database operations
- Error handling
- Job insertion/skipping statistics