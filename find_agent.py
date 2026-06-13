import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
client = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())
print("Agents in this project:")
for a in client.agents.list_agents():
    print(f"  name={a.name!r}  id={a.id}")
