import os
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


BASE_DIR = Path(__file__).resolve().parent
DB_FILENAME = os.environ.get(
    "BASKETBALL_DB_FILE",
    "basketball_live.db",
)

DB_PATH = (BASE_DIR / DB_FILENAME).resolve()

DATABASE_URL = URL.create(
    "sqlite",
    database=DB_PATH.as_uri(),
    # Open an existing database for read/write without creating a new file.
    query={"mode": "rw", "uri": "true"},
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
