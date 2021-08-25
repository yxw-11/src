import os
from pathlib import Path
import sys

from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

PROJECT_ROOT = Path(__file__).parents[1]
BATCH_SIZE = int(os.environ['NER_BATCH_SIZE'])
# SIM_THRESHOLD = float(os.environ['COREF_SIM_THRESHOLD'])
SIM_THRESHOLD = 0.75

if os.environ['ASSETS_PATH'].startswith('/'):
    ASSETS_PATH = os.environ['ASSETS_PATH']
else:
    ASSETS_PATH = PROJECT_ROOT / os.environ['ASSETS_PATH']
MODELS_PATH = ASSETS_PATH / 'models'

DB_CREDS = {
    'dbname': 'ieeedl',
    'user': 'yuxiang',
    'password': 'DxdqpGrT8VdSKPMd',
    'host': 'ieee-capstone.c8hm0l2yjtwy.us-east-1.redshift.amazonaws.com',
    'port': '5439',
}

if __name__ == '__main__':
    key = sys.argv[1]
    ret_val = globals().get(key)
    print(f"{ret_val}")
