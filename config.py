from dotenv import load_dotenv
from datetime import datetime, timedelta

import os


load_dotenv()


conf={
    'dbname':os.getenv('db_name'),
    'user':os.getenv('db_user'),
    'password':os.getenv('db_password'),
    'host':os.getenv('db_host'),
    'port':'6543'
    
}

class Config:
    SQLALCHEMY_DATABASE_URI="postgresql://postgres.ecwdaaciduejggvezkcp:ScrabbleApplicatio@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=20)
    JWT_SECRET_KEY="aurora"
    