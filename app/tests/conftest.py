# import pytest
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.models import Base
# import os
# from dotenv import load_dotenv
# from app.main import get_db

# load_dotenv()

# # Example PostgreSQL database URL format:
# DATABASE_URL_TEST = os.getenv('TEST_DATABASE_URL')

# @pytest.fixture(scope='session')
# def engine():
#     engine = create_engine(DATABASE_URL_TEST)
#     Base.metadata.create_all(engine)  # Create tables at the start of the test session
#     print(f"Engine created with URL: {DATABASE_URL_TEST}")
#     yield engine
#     Base.metadata.drop_all(engine)    # Drop tables at the end of the test session
#     engine.dispose()
#     print("Engine disposed.")

# @pytest.fixture(scope='function')
# def db_session(engine):
#     connection = engine.connect()
#     transaction = connection.begin()
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     yield session

#     session.close()
#     transaction.rollback()
#     connection.close()

# @pytest.fixture(scope='function')
# def client(db_session, monkeypatch):
#     from app.main import app
#     from fastapi.testclient import TestClient

#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             pass

#     monkeypatch.setattr('app.main.get_db', override_get_db)
#     with TestClient(app) as client:
#         yield client