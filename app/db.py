from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path
import os
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
sslrootcert = BASE_DIR / 'ca.pem'

DATABASE_URL = f"postgresql://{os.getenv('USERS')}:{os.getenv('PASSWORD')}@{os.getenv('HOST_NAME')}:{os.getenv('PORT')}/{os.getenv('DATABASE')}"
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
