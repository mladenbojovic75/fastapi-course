from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine, text
from sqlalchemy import pool

from alembic import context

from app.models import Base
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url",f'postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}')
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
#target_metadata = None
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

def ensure_db_exists():
    db_url_without_db = config.get_main_option("sqlalchemy.url").rsplit('/', 1)[0]
    engine = create_engine(db_url_without_db)
    conn = engine.connect()
    try:
        # Check if the database exists
        exists = conn.scalar(text(f"SELECT 1 FROM pg_database WHERE datname = '{settings.database_name}'"))
        if not exists:
            # Close the current connection (which is in a transaction) to create the database
            conn.close()
            # Use a new connection explicitly set to not use transactions
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                connection.execute(text(f'CREATE DATABASE "{settings.database_name}"'))
            print(f"Database '{settings.database_name}' created.")
        else:
            print(f"Database '{settings.database_name}' already exists.")
    except Exception as e:
        print(f"Error checking or creating database: {e}")
    finally:
        conn.close()

# Create Keycloak database
def ensure_db_keycloak_exists():
    db_url_without_db = config.get_main_option("sqlalchemy.url").rsplit('/', 1)[0]
    engine = create_engine(db_url_without_db)
    conn = engine.connect()
    try:
        # Check if the database exists
        exists = conn.scalar(text(f"SELECT 1 FROM pg_database WHERE datname = 'keycloak'"))
        if not exists:
            # Close the current connection (which is in a transaction) to create the database
            conn.close()
            # Use a new connection explicitly set to not use transactions
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
                connection.execute(text(f'CREATE DATABASE "keycloak"'))
            print(f"Database 'keycloak' created.")
        else:
            print(f"Database 'keycloak' already exists.")
    except Exception as e:
        print(f"Error checking or creating database: {e}")
    finally:
        conn.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    ensure_db_keycloak_exists()
    ensure_db_exists()
    run_migrations_online()
