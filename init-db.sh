#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE ${AUTH_DB_NAME:-auth_db};
    CREATE DATABASE ${ORCHESTRATOR_DB_NAME:-orchestrator_db};
EOSQL