# DB_HOST = 'localhost'
# DB_USER = 'root'
# DB_PASSWORD = 'parthsagarjadhav'  # actual password
# DB_NAME = 'resume_scanner'

# UPLOAD_FOLDER = 'uploads'


from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

DB_HOST = os.getenv("locolhost")
DB_USER = os.getenv("root")
DB_PASSWORD = os.getenv("parthsagarjadhav")
DB_NAME = os.getenv("resume_scanner")