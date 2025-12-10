Steps for execution:

1. Run below command to install all required library present in requirements.txt:
pip install -r requirements.txt

2. Update OpenAI API key insideconfig.yaml file and PostGre vector database details inside 'config.yaml' file.

2. Run 'data_scrap.py' file first using below command, to scrap content from the given URL's and generate JSON and save in data.json
python data_scrap.py

4. Setup Postgre Vector database and create table using below query:

"""
    CREATE TABLE amex_pages (
        id SERIAL PRIMARY KEY,
        page_name TEXT,
        page_title TEXT,
        description TEXT,
        page_url TEXT,
        tags TEXT[],
        publish_date TIMESTAMP NULL,
        create_date TIMESTAMP NULL,
        modified_date TIMESTAMP NULL,
        created_by TEXT,
        modified_by TEXT,
        publish_by TEXT,
        locale TEXT,
        page_status TEXT,
        page_scheduled_on_time TIMESTAMP NULL,
        page_scheduled_off_time TIMESTAMP NULL,
        businessUnit TEXT,
        content_owner_email TEXT,
        seo_canonical_url TEXT,
        seo_robots TEXT,
        seo_keywords TEXT[],
        embedding VECTOR(1536)  -- assuming OpenAI embedding dimension
    );
"""

5. Run 'insert_data.py' file to read data.json, create embeddings and insert same  in Postgre vector database.

6. Start Streamlit application using below command:
streamlit run query_data.py


Additional commands to:

    Drop table or delete table:
        DROP TABLE amex_pages;

    Select rows from table:
        SELECT * FROM amex_pages;

    Delete all rows from table
        DELETE FROM amex_pages;


**PostGreSQLTABLE:**

<img width="926" height="397" alt="image" src="https://github.com/user-attachments/assets/905a40b5-de7e-4e5d-a67b-7c4453e4c145" />

<img width="940" height="400" alt="image" src="https://github.com/user-attachments/assets/72443c17-84c9-41ab-b6fa-6f30fa4402d8" />

