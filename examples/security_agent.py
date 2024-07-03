import os

from pandasai.agent.agent import Agent
from pandasai.ee.agents.security_agent import SecurityAgent
from pandasai.llm.openai import OpenAI

os.environ["PANDASAI_API_KEY"] = "$2a****************************"

security = SecurityAgent()
agent = Agent("github-stars.csv", security=security)

print(agent.chat("return total stars count"))


# Using Security standalone
llm = OpenAI("openai_key")
security = SecurityAgent(config={"llm": llm})
security.evaluate("return total github star count for year 2023")
