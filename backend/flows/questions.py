# flows/questions.py

PROCESS_FLOW_QUESTIONS = [
    # NOTE: We don't ask this in UI because user already selected the process.
    # Keep it for exporting (auto-filled from flow.name in backend).
    # {"key": "process_name", "text": "Name of the process", "required": True},

    {"key": "process_owner", "text": "Process owner (job role / name)", "required": True},
    {"key": "process_purpose", "text": "What is the purpose of this process?", "required": True},

    # Narrative / data flow description (keep as one field to avoid overwhelming users)
    {
        "key": "process_flow_narrative",
        "text": "Describe how the data is collected, used, stored, and shared (short story of the flow)",
        "required": True,
    },

    {"key": "data_subjects", "text": "Who are the people the data is about? (data subjects)", "required": True},
    {"key": "data_source", "text": "Where does the data come from? (e.g., employees, customers, third party)", "required": True},

    {"key": "data_collected", "text": "What data do you collect?", "required": True},

    # Data categories + volume (simple wording)
    {
        "key": "personal_data",
        "text": "Personal data used? If yes, list types + volume (Minimal/Low/Medium/High/Very high)",
        "required": True,
    },
    {
        "key": "financial_data",
        "text": "Financial data used? If yes, list types + volume (Minimal/Low/Medium/High/Very high)",
        "required": False,
    },
    {
        "key": "childrens_data",
        "text": "Children’s data used? If yes, list types + volume (Minimal/Low/Medium/High/Very high)",
        "required": False,
    },

    {"key": "lawful_basis", "text": "Lawful basis for processing (e.g., Consent, Contract, Legal obligation, Legitimate interests)", "required": True},

    {
        "key": "special_category_data",
        "text": "Special category / criminal conviction data used? If yes, what type and why?",
        "required": False,
    },

    {"key": "retention", "text": "How long do you keep the data? (retention period)", "required": True},
    {"key": "disposal", "text": "How do you delete/dispose data when no longer needed?", "required": False},

    {"key": "systems_assets", "text": "What systems/tools/folders are used?", "required": True},

    {"key": "who_has_access", "text": "Who can access the data? (job roles)", "required": True},
    {"key": "access_control", "text": "Is access restricted? (Yes/No) If yes, how? (e.g., role-based access)", "required": True},

    {"key": "sharing_internal", "text": "Who do you share the data with inside the organisation (teams/roles)?", "required": False},
    {"key": "third_party_access", "text": "Do any external parties/vendors have access? If yes, who?", "required": False},

    {"key": "outside_uk_eaa", "text": "Is data stored or accessed outside the UK/EAA? (Yes/No) If yes, where?", "required": True},
    {"key": "transborder_agreement", "text": "If outside UK/EAA: is there an agreement in place? (Yes/No/Not sure)", "required": False,
    "depends_on": {"key": "outside_uk_eaa", "value": "yes"}},

    {"key": "org_status", "text": "Organisation’s role for this process: Controller / Joint Controller / Processor", "required": True},

    {"key": "data_shared_other_orgs", "text": "Is data shared with other organisations? (Yes/No)", "required": False},

    {"key": "data_shared_other_orgs_details", "text": "If yes, who is it shared with and why?", "required": False,
    "depends_on": {"key": "data_shared_other_orgs", "value": "yes"}},

    {"key": "data_sharing_agreement", "text": "Is there a data sharing agreement? (Yes/No/Not sure)", "required": False,
    "depends_on": {"key": "data_shared_other_orgs", "value": "yes"}},


    {"key": "outsourced", "text": "Is any part of the process outsourced? (Yes/No) If yes, who?", "required": False},
    {"key": "dpa_in_place", "text": "If outsourced: is there a data processing agreement (DPA)? (Yes/No/Not sure)", "required": False,
     "depends_on": {"key": "outsourced", "value": "yes"}},

    {"key": "adm", "text": "Is automatic decision-making used? (Yes/No) If yes, describe", "required": False},

    {"key": "other_info", "text": "Any other relevant information", "required": False},
]
