"""Working with data: terminal tools for files and databases, and the VS Code side."""

from rigsmith.backends import UvTool
from rigsmith.library._util import ext, tool

tool("duckdb", 'In-process analytical SQL: query CSV/Parquet/JSON files directly. `duckdb -c "select …"`.')
tool("pgcli", "Postgres CLI with autocompletion and syntax highlighting.")
tool("miller", "awk/sed/jq for CSV, TSV and JSON records: `mlr --icsv --opprint cat`.", bin="mlr")
tool("visidata", "Terminal spreadsheet for exploring any tabular data: `vd file.csv`.", bin="vd", tags=["tui"])
tool("lazysql", "Terminal UI for SQL databases (Postgres, MySQL, SQLite).", tags=["tui"])
tool("harlequin", "SQL IDE in the terminal (DuckDB, SQLite, Postgres…).", sources=[UvTool("harlequin")], tags=["tui"])
tool("kcat", "Kafka swiss-army knife: produce, consume, inspect topics.")

ext("rainbow-csv", "mechatroner.rainbow-csv", "Color CSV columns and query them with SQL-like RBQL.")
ext("sqltools", "mtxr.sqltools", "SQL client in VS Code (add a driver: sqltools-pg, sqltools-mysql).")
ext("sqltools-pg", "mtxr.sqltools-driver-pg", "PostgreSQL driver for SQLTools.", requires=["vscode", "sqltools"])
ext("sqltools-mysql", "mtxr.sqltools-driver-mysql", "MySQL driver for SQLTools.", requires=["vscode", "sqltools"])
ext("mongodb-ext", "mongodb.mongodb-vscode", "MongoDB: browse data and run queries in VS Code.")
ext("redis-ext", "Redis.redis-for-vscode", "Redis: browse keys and run commands in VS Code.")
ext("sqlite-viewer", "qwtel.sqlite-viewer", "Open SQLite databases as tables.")
ext("database-client", "cweijan.vscode-database-client2", "Multi-database client (MySQL, Postgres, Redis, Mongo…).")
