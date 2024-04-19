#!/bin/bash -e
# start script
CRONMODE=${CRONMODE:-false}
if $CRONMODE; then
  if [ -z "${CRON_EXPRESSION}" ]; then
    echo 'ERROR: The environment variable CRON_EXPRESSION must be specified in cron mode.'
    exit 255
  fi
  echo "${CRON_EXPRESSION} /venv/bin/python3 /backup.py $@" >/var/spool/cron/crontabs/root
  echo "=== started in cron mode $(/bin/date "+%Y/%m/%d %H:%M:%S") ==="
  crontab -l
  exec crond -f -d 8
else
  exec /venv/bin/python3 /backup.py $@
fi
