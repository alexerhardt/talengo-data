import os
import json
import simple_salesforce
from dotenv import load_dotenv

load_dotenv()

SF_PROD_USERNAME = os.getenv('SF_PROD_USERNAME')
SF_PROD_PASSWORD = os.getenv('SF_PROD_PASSWORD')
SF_PROD_SECURITY_TOKEN = os.getenv('SF_PROD_SECURITY_TOKEN')

path_in = os.path.join(os.path.dirname(__file__), 'data/model.json')
path_out = os.path.join(os.path.dirname(__file__), 'data/relations.json')

with open(path_in) as f:
    models = json.load(f)
    object_names = list(models.keys())

sf_prod = simple_salesforce.Salesforce(username=SF_PROD_USERNAME,
                                       password=SF_PROD_PASSWORD,
                                       security_token=SF_PROD_SECURITY_TOKEN)

object_rels_map = {}

for object_name in object_names:
    fields_metadata = sf_prod.__getattr__(object_name).describe()
    fields = [(field['name'], field['referenceTo']) for field in
              fields_metadata['fields']
              if
              field['createable'] and field['type'] == 'reference']

    for field in fields:
        object_rels_map.setdefault(object_name, {})[field[0]] = field[1]

with open(path_out, 'w') as f:
    json.dump(object_rels_map, f, indent=2)
