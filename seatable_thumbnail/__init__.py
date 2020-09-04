from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import seatable_thumbnail.settings as settings

db_url = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % \
    (settings.MYSQL_USER, settings.MYSQL_PASSWORD,
     settings.MYSQL_HOST, settings.MYSQL_PORT, settings.DATABASE_NAME)
db_kwargs = dict(pool_recycle=300, echo=False, echo_pool=False)

engine = create_engine(db_url, **db_kwargs)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
