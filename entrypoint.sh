#!/bin/sh

if [ "$1" = -- ]; then
    shift
    exec "$@"
fi

if [ $# -eq 0 ]; then
    set trace
fi

exec python3 -m ctrace "$@"
