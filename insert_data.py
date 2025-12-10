import openai
import json
from datetime import datetime
from database_connector.postgre_connector import get_db_connection, get_cursor, close_connection
from config.config_loader import OPENAI_CONFIG

openai.api_key = OPENAI_CONFIG["api_key"]

conn = get_db_connection()
cursor = get_cursor(conn)

# Read JSON array
with open("data.json", "r") as file:
    json_array = json.load(file)

# Convert Python list → pgvector string
def to_pgvector(embedding):
    return "[" + ",".join(str(x) for x in embedding) + "]"

def safe_date(value):
    """Convert empty string to None for TEXT/TIMESTAMP fields."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value 

for page_data in json_array:

    # Build content for embedding
    text_for_embedding = (
        f"{page_data['page_name']} "
        f"{page_data['page_title']} "
        f"{page_data['description']} "
        f"{page_data['page_url']} "
        f"{' '.join(page_data['tags'])} "
        f"{page_data['publish_date']} "
        f"{page_data['create_date']} "
        f"{page_data['modified_date']} "
        f"{page_data['created_by']} "
        f"{page_data['modified_by']} "
        f"{page_data['publish_by']} "
        f"{page_data['locale']} "
        f"{page_data['page_status']} "
        f"{page_data['page_scheduled_on_time']} "
        f"{page_data['page_scheduled_off_time']} "
        f"{page_data['businessUnit']} "
        f"{page_data['content_owner_email']} "
        f"{page_data['seo']['canonical_url']} "
        f"{page_data['seo']['robots']} "
        f"{' '.join(page_data['seo']['seo_keywords'])}"
    )

    # Generate OpenAI embedding
    emb_response = openai.embeddings.create(
        input=text_for_embedding,
        model="text-embedding-3-small"
    )

    embedding_vector = emb_response.data[0].embedding
    embedding_pg = to_pgvector(embedding_vector)

    # SQL insert
    insert_query = """
    INSERT INTO amex_pages (
        page_name, page_title, description, page_url, tags, publish_date, create_date,
        modified_date, created_by, modified_by, publish_by, locale, page_status,
        page_scheduled_on_time, page_scheduled_off_time, businessUnit, content_owner_email,
        seo_canonical_url, seo_robots, seo_keywords, embedding
    ) VALUES (
        %(page_name)s, %(page_title)s, %(description)s, %(page_url)s, %(tags)s,
        %(publish_date)s, %(create_date)s, %(modified_date)s, %(created_by)s,
        %(modified_by)s, %(publish_by)s, %(locale)s, %(page_status)s,
        %(page_scheduled_on_time)s, %(page_scheduled_off_time)s, %(businessUnit)s,
        %(content_owner_email)s, %(seo_canonical_url)s, %(seo_robots)s,
        %(seo_keywords)s, %(embedding)s
    );
    """
    
    cursor.execute(insert_query, {
        "page_name": page_data["page_name"],
        "page_title": page_data["page_title"],
        "description": page_data["description"],
        "page_url": page_data["page_url"],
        "tags": page_data["tags"],

        # FIXED HERE: safe_date() prevents ""
        "publish_date": safe_date(page_data["publish_date"]),
        "create_date": safe_date(page_data["create_date"]),
        "modified_date": safe_date(page_data["modified_date"]),

        "created_by": page_data["created_by"],
        "modified_by": page_data["modified_by"],
        "publish_by": page_data["publish_by"],
        "locale": page_data["locale"],
        "page_status": page_data["page_status"],

        "page_scheduled_on_time": safe_date(page_data["page_scheduled_on_time"]),
        "page_scheduled_off_time": safe_date(page_data["page_scheduled_off_time"]),

        "businessUnit": page_data["businessUnit"],
        "content_owner_email": page_data["content_owner_email"],
        "seo_canonical_url": page_data["seo"]["canonical_url"],
        "seo_robots": page_data["seo"]["robots"],
        "seo_keywords": page_data["seo"]["seo_keywords"],
        "embedding": embedding_pg
    })

close_connection(conn, cursor)

print("All page data + embeddings inserted successfully!")
