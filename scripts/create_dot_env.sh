#!/bin/bash

ENV=$1
DOT_ENV=".env"

# postgres password
POSTGRES_DOT_ENV=".env.postgres.$ENV"
POSTGRES_PASSWORD=`openssl rand -hex 32`
if test -f "$POSTGRES_DOT_ENV"; then
    if [[ `cat "$POSTGRES_DOT_ENV"` =~ .*=\"(.*)\" ]]; then
        POSTGRES_PASSWORD=${BASH_REMATCH[1]}
    fi 
fi
echo POSTGRES_PASSWORD=\""$POSTGRES_PASSWORD"\" > .env.postgres
echo POSTGRES_PASSWORD=\""$POSTGRES_PASSWORD"\" > "$POSTGRES_DOT_ENV"

# JWT key
echo CODEMAZE_KEY=\"$(openssl rand -base64 32)\" > "$DOT_ENV"

# DB address
DB_ADDRESS="localhost:5432"
if [ "$ENV" = "deploy" ]; then
    DB_ADDRESS="postgres:5432"
fi
echo CODEMAZE_DB_STRING=\"postgresql://codemaze:"$POSTGRES_PASSWORD"@"$DB_ADDRESS"/codemaze_db\" >> "$DOT_ENV"

# custom keys
ENV_DOT_ENV=".env.$ENV"
if test -f "$ENV_DOT_ENV"; then
    cat "$ENV_DOT_ENV" >> "$DOT_ENV"
fi

# runner max memory allowed
MEM_ALLOWED=`cat config.toml | grep max-memory-mb | awk -F '=' '{print $2}'`
echo RUNNER_MAX_MEM=\""$MEM_ALLOWED"\" >> "$DOT_ENV"
