Necessary pre-conditions for data migration:

- Run create metadata to add ProductionId fields to all objects
- Run products script to copy over production ids
- Sync all Pricebook ProductionIds (they're pre-created on migrate); should create script
- Disable all duplicate detection rules
- Disable Order validation rules
- Disable Order flow validation "Activación Cliente Nuevo"
- Disable Quote ("Propuesta") trigger named "Propuesta"
- Disable reglas de flujo de trabajo
- Disable Apex trigger de Contact
