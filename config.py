from dotenv import load_dotenv
from datetime import datetime, timedelta

import os

load_dotenv()

conf={
    'dbname':'postgres',
    'user':'postgres.ecwdaaciduejggvezkcp',
    'password':'ScrabbleApplicatio',
    'host':'aws-0-us-east-1.pooler.supabase.com',
    'port':'6543'
}

class Config:
    SQLALCHEMY_DATABASE_URI=f"postgresql://{conf['user']}:{conf['password']}@{conf['host']}:5432/postgres"
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=20)
    JWT_SECRET_KEY=os.getenv('jwt_secret_key')