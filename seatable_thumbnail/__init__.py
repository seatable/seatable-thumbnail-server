from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import redis

import seatable_thumbnail.settings as settings

db_url = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % \
    (settings.MYSQL_USER, settings.MYSQL_PASSWORD,
     settings.MYSQL_HOST, settings.MYSQL_PORT, settings.DATABASE_NAME)
db_kwargs = dict(pool_recycle=300, echo=False, echo_pool=False)

engine = create_engine(db_url, **db_kwargs)
class Base(DeclarativeBase):
    pass
DBSession = sessionmaker(bind=engine)


redis_client = redis.Redis(host=settings.REDIS_HOST, decode_responses=True)
