from config import get_sf_sandbox, get_object_model, PRODUCTION_ID_KEY

sf = get_sf_sandbox()
object_model = get_object_model()
# This was ridiculously hard to find
# https://salesforce.stackexchange.com/questions/159005/listing-of-all-standard-profiles-and-their-metadata-api-names
PROFILE_NAME = "Admin"

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
        externalId=True,
    )

    # Create the custom field in Salesforce
    try:
        mdapi.CustomField.upsert(custom_field)
        print(f"{field_name} upserted successfully")
    except Exception as e:
        print(f"Error creating {field_name}: {e}")

    permission_set = mdapi.Profile(
        fullName=PROFILE_NAME,
        fieldPermissions=[
            mdapi.ProfileFieldLevelSecurity(
                field=field_name, readable=True, editable=True
            )
        ],
    )

    try:
        mdapi.Profile.update(permission_set)
        print(f"Permission set for {field_name} updated successfully")
    except Exception as e:
        print(f"Error creating permission set for {field_name}: {e}")
