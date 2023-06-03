#!/usr/bin/bash
cd "$(dirname "$0")"
/usr/local/bin/supervisord -c ./supervisord.conf
