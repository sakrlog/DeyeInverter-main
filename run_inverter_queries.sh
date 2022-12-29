#!/usr/bin/bash 

until python3.9 InverterQueries.py; do
    echo "Server 'InverterQueries.py' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done