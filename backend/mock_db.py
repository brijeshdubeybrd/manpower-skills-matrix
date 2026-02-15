import random

# Constants for generating realistic data
GROUPS = ["Aditya Birla Group", "Tata Group", "Reliance Industries"]
SBUS = ["Cement", "Retail", "Telecom", "Financial Services"]
BUS = ["UltraTech", "Pantaloons", "Jio", "Aditya Birla Capital"]
FUNCTIONS = ["Engineering", "Sales", "HR", "Finance", "Marketing"]
BANDS = ["E1", "E2", "E3", "M1", "M2", "M3"]
L1_UJRS = ["Managerial", "Operational", "Strategic"]
COMPETENCY_TYPES = ["Functional", "Behavioral", "Technical"]

SKILLS = {
    "Engineering": [
        ("Python Automation", "Ability to script tasks and automate workflows using Python."),
        ("System Design", "Designing scalable and reliable software systems."),
        ("Cloud Infrastructure", "Managing AWS/Azure resources efficiently."),
        ("DevOps", "CI/CD pipeline management and containerization."),
    ],
    "Sales": [
        ("Negotiation", "Ability to close deals and manage client expectations."),
        ("CRM Management", "Proficiency in Salesforce or HubSpot."),
        ("Lead Generation", "Identifying and cultivating potential customers."),
        ("Solution Selling", "Diagnosing customer needs and recommending products."),
    ],
    "HR": [
        ("Talent Acquisition", "Sourcing and hiring top talent."),
        ("Employee Relations", "Managing conflict resolution and employee engagement."),
        ("Payroll Management", "Processing salaries and benefits."),
        ("Training & Development", "Designing and delivering training programs."),
    ],
    "Finance": [
        ("Financial Modeling", "Building financial models for forecasting."),
        ("Tax Compliance", "Ensuring adherence to tax laws and regulations."),
        ("Auditing", " examining financial records for accuracy."),
        ("Budgeting", "Planning and allocating financial resources."),
    ],
    "Marketing": [
        ("SEO/SEM", "Optimizing content for search engines."),
        ("Content Strategy", "Planning and creating engaging content."),
        ("Social Media Marketing", "Managing brand presence on social platforms."),
        ("Market Research", "Analyzing market trends and competitor activity."),
    ]
}

def generate_mock_data(num_records=60):
    data = []
    for i in range(num_records):
        func = random.choice(FUNCTIONS)
        skill_name, skill_def = random.choice(SKILLS[func])
        
        record = {
            "id": i + 1,  # Added ID for frontend key/editing
            "Group": random.choice(GROUPS),
            "SBU": random.choice(SBUS),
            "BU": random.choice(BUS),
            "Function": func,
            "UJR_in_UJR_Master": f"{func[:3].upper()}_{random.choice(BANDS)}_{i:03d}",
            "Job_Role_Name_without_concat": f"{func} {random.choice(['Executive', 'Manager', 'Analyst', 'Specialist'])}",
            "L1_UJR": random.choice(L1_UJRS),
            "Competency_Type": random.choice(COMPETENCY_TYPES),
            "Skill_Name": skill_name,
            "Skill_Definition": skill_def,
            "Proficiency_Level": str(random.randint(1, 5)),
            "Band": random.choice(BANDS)
        }
        data.append(record)
    return data

# Initialize the mock database with 60 records
MOCK_DB = generate_mock_data(60)

def get_db():
    return MOCK_DB

def reset_db():
    global MOCK_DB
    MOCK_DB = generate_mock_data(60)
    return MOCK_DB
