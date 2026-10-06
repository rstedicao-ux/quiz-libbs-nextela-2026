import os
import sys

# Re-export everything from api.db
current_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.join(current_dir, 'api')
for p in [current_dir, api_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from api.db import (
    get_db, init_db, json_response, options_response,
    GABARITO, get_postgres_url, PSYCOPG2_AVAILABLE
)
