"""Working with data files and databases in VS Code."""

from rigsmith.library._util import ext

ext("rainbow-csv", "mechatroner.rainbow-csv", "Color CSV columns and query them with SQL-like RBQL.")
ext("sqltools", "mtxr.sqltools", "SQL client in VS Code (add a driver: sqltools-pg, sqltools-mysql).")
ext("sqltools-pg", "mtxr.sqltools-driver-pg", "PostgreSQL driver for SQLTools.", requires=["vscode", "sqltools"])
ext("sqltools-mysql", "mtxr.sqltools-driver-mysql", "MySQL driver for SQLTools.", requires=["vscode", "sqltools"])
ext("mongodb-ext", "mongodb.mongodb-vscode", "MongoDB: browse data and run queries in VS Code.")
ext("redis-ext", "Redis.redis-for-vscode", "Redis: browse keys and run commands in VS Code.")
ext("sqlite-viewer", "qwtel.sqlite-viewer", "Open SQLite databases as tables.")
ext("database-client", "cweijan.vscode-database-client2", "Multi-database client (MySQL, Postgres, Redis, Mongo…).")
