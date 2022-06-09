import os

import dotenv

dotenv.load_dotenv()

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")  # ASANA API CLIENT ACCESS TOKEN
POSTGRES_URL = os.environ.get("POSTGRES_URL")  # POSTGRESQL SQLAlchemy connection string
