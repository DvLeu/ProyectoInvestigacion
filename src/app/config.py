import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:tu_password@localhost:3307/asistencia_automation"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
