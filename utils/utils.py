import random
from urllib.parse import urlparse
import openai

def get_locale_from_url(url: str) -> str | None:
    parsed = urlparse(url)
    parts = parsed.path.split("/")
    if len(parts) >= 2 and parts[1].startswith("en-"):
        return parts[1]
    return None

def random_time():
    """Generate a random time string HH:MM:SS"""
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return hour, minute, second

def random_name():
    names = ["Doug", "Amy", "Jack", "Mike", "Robert", "Jennifer", "Adam", "Andre", "Anna"]

    # 2️⃣ Pick a random name
    return random.choice(names)

def random_email():
    names = ["doug@test.com", "amy@test.com", "jack@test.com", "mike@test.com", "robert@test.com", "jennifer@test.com", "adam@test.com", "andre@test.com", "anna@test.com"]

    # Pick a random name email
    return random.choice(names)

def embed_text(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding