#!/bin/bash

############################################################################
# Container Entrypoint script
############################################################################

if [[ "$PRINT_ENV_ON_LOAD" = true || "$PRINT_ENV_ON_LOAD" = True ]]; then
  echo "=================================================="
  printenv
  echo "=================================================="
fi

if [[ "$WAIT_FOR_DB" = true || "$WAIT_FOR_DB" = True ]]; then
  dockerize \
    -wait tcp://$DB_HOST:$DB_PORT \
    -timeout 300s
fi

############################################################################
# Load F1 Data
############################################################################

if [[ "$LOAD_F1_DATA" = true || "$LOAD_F1_DATA" = True ]]; then
  echo "Loading F1 data into database..."
  python scripts/load_f1_data.py
  
  echo "Loading F1 metadata into knowledge base..."
  python -m teams.data_analysis_team
fi

############################################################################
# Start App
############################################################################

case "$1" in
  chill)
    ;;
  *)
    echo "Running: $@"
    exec "$@"
    ;;
esac

echo ">>> Hello World!"
while true; do sleep 18000; done
