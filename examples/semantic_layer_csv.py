import pandasai as pai

# read data from your csv
df = pai.read_csv("./data/heart.csv")

# enrich your dataframe with semantic information
# path must be in format 'organization/dataset'
# columns must be in format [{'name': 'column_name', 'type': 'column_type', 'description': 'column_description'}]
df.save(path="your-organization/heart",
    name="Heart",
    description="Heart Disease Dataset",
    columns=[
        {
            "name": "Age",
            "type": "number",
            "description": "Age of the patient in years"
        },
        {
            "name": "Sex",
            "type": "string",
            "description": "Gender of the patient (M: Male, F: Female)"
        },
        {
            "name": "ChestPainType",
            "type": "string",
            "description": "Type of chest pain (ATA: Atypical Angina, NAP: Non-Anginal Pain, ASY: Asymptomatic, TA: Typical Angina)"
        },
        {
            "name": "RestingBP",
            "type": "number",
            "description": "Resting blood pressure in mm Hg"
        },
        {
            "name": "Cholesterol",
            "type": "number",
            "description": "Serum cholesterol in mg/dl"
        },
        {
            "name": "FastingBS",
            "type": "number",
            "description": "Fasting blood sugar (1: if FastingBS > 120 mg/dl, 0: otherwise)"
        },
        {
            "name": "RestingECG",
            "type": "string",
            "description": "Resting electrocardiogram results (Normal, ST: having ST-T wave abnormality, LVH: showing probable or definite left ventricular hypertrophy)"
        },
        {
            "name": "MaxHR",
            "type": "number",
            "description": "Maximum heart rate achieved"
        },
        {
            "name": "ExerciseAngina",
            "type": "string",
            "description": "Exercise-induced angina (Y: Yes, N: No)"
        },
        {
            "name": "Oldpeak",
            "type": "number",
            "description": "ST depression induced by exercise relative to rest"
        },
        {
            "name": "ST_Slope",
            "type": "string",
            "description": "Slope of the peak exercise ST segment (Up, Flat, Down)"
        },
        {
            "name": "HeartDisease",
            "type": "number",
            "description": "Target variable - Heart disease presence (1: heart disease, 0: normal)"
        }
    ])

# once you have saved the dataframe, you can load it across sessions
df = pai.load("your-organization/heart")