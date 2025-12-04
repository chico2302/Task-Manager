import os
from dotenv import load_dotenv
load_dotenv()

#infos do BD
class Config:
    DB_HOST = os.getenv("DB_HOST","localhost")
    DB_USER = os.getenv("DB_USER","root")
    DB_PASSWORD = os.getenv("DB_PASSWORD","senha")
    DB_NAME = os.getenv("DB_NAME","todo_app")

    #configs do servidor o7
    PORT = int(os.getenv("PORT","3000"))
    DEBUG = os.getenv("DEBUG","FALSE").lower() == "true"

    @property
    def config_bd(self):
        return{
            'host':self.DB_HOST,
            'user':self.DB_USER,
            'password':self.DB_PASSWORD,
            'database':self.DB_NAME,
            'charset':'utf8mb4',
            'autocommit':True
        }
