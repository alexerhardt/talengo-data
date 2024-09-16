from config import get_sf_sandbox

sf = get_sf_sandbox()

query = "SELECT Id FROM OpportunityTeamMember WHERE User.email = 'ae@alexerhardt.com'"
records = sf.query_all(query)["records"]

for record in records:
    print(f"Deleting OpportunityTeamMember {record['Id']}")
    sf.OpportunityTeamMember.delete(record["Id"])
