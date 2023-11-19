import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
load_dotenv()

# Load data from aw-buckets-export.json
with open('aw-buckets-export.json', 'r') as file:
    productivity_data = json.load(file)

client = AzureOpenAI(
  azure_endpoint = 'https://api.umgpt.umich.edu/azure-openai-api/ptu',
  api_key=os.getenv("apikey"),  
  api_version="2023-03-15-preview"
)

response = client.chat.completions.create(
    model="gpt-4", # model = "deployment_name".
    messages=[
        {"role": "system", "content": "You provide helpful productivity advice to improve study and work habits"},
        {"role": "assistant", "content": "Please provide your activity data and I will give you concise yet insightful analysis."},
        {"role": "user", "content": f"{productivity_data}"}
    ]
)

print(response.choices[0].message.content)