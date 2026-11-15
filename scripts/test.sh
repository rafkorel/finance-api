#!/usr/bin/env bash
set -e

unset DATABASE_URL
source ./.env.test

if [[ -z "$DATABASE_URL" ]]; then
    echo "В .env.test не задан DATABASE_URL" >&2
    exit 1
fi

export DATABASE_URL
exec python -m pytest "$@"