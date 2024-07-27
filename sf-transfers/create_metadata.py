from config import get_sf_sandbox, get_object_model, PRODUCTION_ID_KEY

sf = get_sf_sandbox()
object_model = get_object_model()

mdapi = sf.mdapi

for object_key in object_model.keys():
    field_name = f"{object_key}.{PRODUCTION_ID_KEY}"

    custom_field = mdapi.CustomField(
        fullName=f"{field_name}",
        label="Production ID",
        type=mdapi.FieldType("Text"),
        length=18,  # Salesforce record IDs are 18 characters
        inlineHelpText="Original ID from Production environment",
        unique=True,
    )

    # Create the custom field in Salesforce
    try:
        mdapi.CustomField.create(custom_field)
        print(f"{field_name} created successfully")
    except Exception as e:
        print(f"Error creating {field_name}: {e}")
