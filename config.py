class Config:
    def __init__(self):
        self.DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:example_pawDB.!@localhost:3307/TM_v2'