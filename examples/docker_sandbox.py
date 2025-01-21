# Install pandasai docker using
# pip install pandasai-docker
from pandasai_docker import DockerSandbox
from pandasai_openai.openai import OpenAI

import pandasai as pai

llm = OpenAI(api_token="sk-*******")

pai.config.set({"llm": llm})

df = pai.read_csv("/Users/arslan/Documents/SinapTik/pandas-ai/artists.csv")


sandbox = DockerSandbox()
agent = Agent([df], memory_size=10, sandbox=sandbox)
# Chat with the Agent
response = agent.chat("plot top five artists streams")

# destroy container after usage or let class destructor destroys it.
sanbox.stop()


# Use custom docker image
sandbox = DockerSandbox("pandaai-sandbox", "/path/to/Dockerfile")
agent = Agent([df], memory_size=10, sandbox=sandbox)
# Chat with the Agent
response = agent.chat("plot top five artists streams")

# destroy container after usage or let class destructor destroys it.
sandbox.stop()
