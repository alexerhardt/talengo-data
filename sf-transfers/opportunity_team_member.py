from config import get_sf_prod, get_sf_sandbox, get_object_model
from migrate import migrate

sf_prod = get_sf_prod()
sf_sandbox = get_sf_sandbox()
object_model = get_object_model()

query = "SELECT Id FROM OpportunityTeamMember WHERE User.IsActive = true AND Opportunity.StageName != 'Closed Lost' AND Opportunity.CloseDate >= 2021-01-01"

migrate(sf_prod, sf_sandbox, "OpportunityTeamMember", object_model, query)
