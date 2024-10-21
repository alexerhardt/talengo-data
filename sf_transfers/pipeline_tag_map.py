def map_pipeline_tags(row):
    uninterested = row["Declined__c"]
    discarded = row["Estatus__c"] == "Descartado" or row["Rejected__c"]
    match row["Fase__c"]:
        case "1- Inicial":
            if uninterested:
                return "3. Initial filter (not interested)"
            if discarded:
                return "3. Initial filter (discarded)"
            else:
                return "1. Identified"
        case "2- Entrevista Telefónica":
            if uninterested:
                return "3. Initial filter (not interested)"
            if discarded:
                return "3. Initial filter (discarded)"
            else:
                return "3. Initial filter (done - standby)"
        case "3- Entrevista Presencial" | "4- Long list":
            if uninterested:
                return "3- Talengo interview (not interested)"
            if discarded:
                return "3- Talengo interview (discarded)"
            else:
                return "3- Talengo interview (done - standby)"
        case "5- Entrevista con el Cliente (Lista Corta)":
            if uninterested:
                return "5. Client interview (not interested)"
            if discarded:
                return "5. Client interview (discarded)"
            else:
                return "5. Client interview (shortlisted)"
        case "6- Toma de referencias" | "7- Candidato finalista":
            offer_status = row["OfferAccepted__c"]
            if offer_status == "Aceptada":
                return "7. Placement"
            elif offer_status == "Rechazada":
                return "6. Offer made (rejected)"
            else:
                return "5. Client interview (discarded)"
            if uninterested:
                return "5. Client interview (not interested)"
            else:
                return "5. Client interview (discarded)"
