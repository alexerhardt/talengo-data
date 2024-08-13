from config import get_sf_sandbox, get_object_model, PRODUCTION_ID_KEY

sf = get_sf_sandbox()
object_model = get_object_model()

mdapi = sf.mdapi

# Iterate through each object in the model and delete the ProductionId__c field
for object_key in object_model.keys():
    field_name = f"{object_key}.{PRODUCTION_ID_KEY}"

    try:
        # Delete the custom field
        mdapi.CustomField.delete(field_name)
        print(f"Deleted field: {field_name}")
    except Exception as e:
        print(f"Error deleting field {field_name}: {e}")
