# Saleforce Data Migration Scripts

These scripts were developed in order to migrate data from Salesforce prod to sandbox
environments.

The scripts copy an entire collection of objects, given a Salesforce object key
(ex: "Contact", "Improvement"), along with its references in depth. For example,
if a Contact has an Account relationship, it will copy that data, too.

Why didn't I use dataloader, or some other utility, you ask?

Well first, we don't do these things because they're easy - we do them because we 
thought they would be easy.

But also, I tried dataloader, and for the task I needed to accomplish - copying some
deeply-seated SF objects - it didn't work in a few clicks, and it threw all sort of 
errors. Why would I pay for that shit?

## Code tour

- /data: Includes a few config objects and useful samples
- /metadata: Scripts relating to metadata copying between SF instances
- migrate.py: Entry point
- upsert_record.py


## Order of operations

### Migrating 

- Run create metadata to add ProductionId fields to all objects
- Run products script to copy over production ids
- Sync all Pricebook ProductionIds (they're pre-created on migrate)
- Disable all triggers, validation rules, and flows which might get in your way
- Run the migrate script 

### Disabling stuff

I had to disable a bunch of stuff for this to work. Here's a little log.

I think this generally doesn't affect anything. Most triggers and such write derived
data and enforce validation, but you don't need any of that in a migration.

- Disable all duplicate detection rules (reglas duplicadas, reglas de coincidencia)
- Disable Order validation rules
- Disable Order flow validation "Activación Cliente Nuevo"
- Disable Quote ("Propuesta") trigger named "Propuesta"
- Disable Apex trigger de Contact
  This removes errors with some address migrations. However it doesn't create the CV.
- Disable reglas de flujo de trabajo?
- Disable flujo Equipo de Trabajo
- Disable Equipo Proceso (not sure if necessary)
- Re-enable old currencies



## Areas to improve

- Add testing with pytest (challenge: lots of mocking)
- upsert_record.py has plenty of smells
- Better logging throughout
