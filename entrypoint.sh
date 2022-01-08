#!/bin/sh

if [ "$1" = -- ]; then
    shift
    exec "$@"
fi

exec python3 -m ctrace "$@"
