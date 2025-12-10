import streamlit as st
import openai
import json

from datetime import datetime
from database_connector.postgre_connector import get_connection, get_cursor, close_connection, embed_text 
from config.config_loader import OPENAI_CONFIG

openai.api_key = OPENAI_CONFIG["api_key"]

# -----------------------------
# Helpers
# -----------------------------
def to_pgvector(embedding):
    return "[" + ",".join(str(x) for x in embedding) + "]"

def safe_date(value):
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    return value

conn = get_connection()
cursor = get_cursor(conn)

def search_similar_pages(query_embedding):
    sql = """
        SELECT 
            id,
            page_name,
            page_title,
            description,
            page_url,
            tags,
            publish_date,
            create_date,
            modified_date,
            created_by,
            modified_by,
            publish_by,
            locale,
            page_status,
            businessUnit,
            content_owner_email,
            seo_canonical_url,
            seo_robots,
            seo_keywords,
            embedding <-> %s::vector AS distance
        FROM amex_pages
        ORDER BY embedding <-> %s::vector;
    """
    vector_literal = to_pgvector(query_embedding)
    cursor.execute(sql, (vector_literal, vector_literal))
    rows = cursor.fetchall()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "page_name": r[1],
            "page_title": r[2],
            "description": r[3],
            "page_url": r[4],
            "tags": r[5],
            "publish_date": r[6],
            "create_date": r[7],
            "modified_date": r[8],
            "created_by": r[9],
            "modified_by": r[10],
            "publish_by": r[11],
            "locale": r[12],
            "page_status": r[13],
            "businessUnit": r[14],
            "content_owner_email": r[15],
            "seo_canonical_url": r[16],
            "seo_robots": r[17],
            "seo_keywords": r[18],
            "similarity_score": float(r[19])
        })
    return results

def filter_fields_by_query(query, retrieved_pages):
    if not retrieved_pages:
        return []

    system_prompt = """
        You are a metadata field selector for web pages. 
        Given a user question and a JSON object containing 
        page metadata fields (e.g., page_name, page_title, description, 
        publish_date, create_date, modified_date, created_by, locale, 
        tags, SEO fields, etc.), your task is to return ONLY the field 
        names that are relevant to answer the user's question. 
        Output format: JSON array of field names. Do NOT include any 
        explanations, commentary, or additional text.
    """

    user_prompt = f"""
    USER QUESTION:
    {query}

    AVAILABLE FIELDS:
    {list(retrieved_pages[0].keys())}
    """

    response = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    try:
        selected_fields = json.loads(response.choices[0].message.content)
        return selected_fields
    except Exception as e:
        st.warning(f"Failed to parse selected fields: {e}")
        return list(retrieved_pages[0].keys())

def rag_answer(query):
    query_emb = embed_text(query)
    pages = search_similar_pages(query_emb)
    if not pages:
        return "No matching data found."

    fields_needed = filter_fields_by_query(query, pages)

    context = []
    for p in pages:
        filtered = {k: p[k] for k in fields_needed if k in p}
        for k, v in filtered.items():
            if isinstance(v, datetime):
                filtered[k] = v.isoformat()
        context.append(filtered)

    final_prompt = f"""
    Answer the user's question using ONLY the following filtered data:

    {json.dumps(context, indent=2)}

    USER QUESTION:
    {query}
    """

    answer = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Number of page published."},
            {"role": "user", "content": final_prompt}
        ]
    )

    return answer.choices[0].message.content

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="RAG for AMEX Pages", layout="wide")
st.title("AMEX Pages RAG Chat")

query = st.text_input("Enter your query here:", "")

if st.button("Get Answer") and query.strip():
    with st.spinner("Fetching answer..."):
        response = rag_answer(query)
        st.success("Done!")
        st.markdown("### Answer")
        st.write(response)