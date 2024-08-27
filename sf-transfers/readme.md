Necessary pre-conditions for data migration:

- Run create metadata to add ProductionId fields to all objects
- Run products script to copy over production ids
- Sync all Pricebook ProductionIds (they're pre-created on migrate)
- Disable all duplicate detection rules (reglas duplicadas, reglas de coincidencia)
- Disable Order validation rules
- Disable Order flow validation "Activación Cliente Nuevo"
- Disable Quote ("Propuesta") trigger named "Propuesta"
- Disable Apex trigger de Contact
  This removes errors with some address migrations. However it doesn't create the CV.
- Disable reglas de flujo de trabajo?
- Activate inactive users (temporally); disable ResearchMad in sandbox
  - Ricardo Herrera
- Disable flujo Equipo de Trabajo
- Disable Equipo Proceso (not sure if necessary)
