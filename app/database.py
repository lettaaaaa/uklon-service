from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os


# Для локальной разработки используется обычный DATABASE_URL
# Для Cloud Run используется подключение через Unix socket
def get_database_url():
    # Проверяем, запущено ли приложение в Cloud Run
    if os.getenv("CLOUD_SQL_CONNECTION_NAME"):
        # Подключение через Unix socket для Cloud SQL
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "taxi_db")
        instance_connection_name = os.getenv("CLOUD_SQL_CONNECTION_NAME")

        # Unix socket путь для Cloud SQL
        unix_socket_path = f"/cloudsql/{instance_connection_name}"

        return f"postgresql+asyncpg://{db_user}:{db_password}@/{db_name}?host={unix_socket_path}"
    else:
        # Локальная разработка - обычный DATABASE_URL
        return os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/taxi_db")


DATABASE_URL = get_database_url()

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with async_session_maker() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
