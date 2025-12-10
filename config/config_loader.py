import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

DB_CONFIG = config["database"]
OPENAI_CONFIG = config["openai"]
