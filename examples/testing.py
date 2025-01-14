import os
import pandasai as pai
from pandasai_openai import OpenAI

os.environ["PANDABI_API_URL"] = "https://api.pandabi.ai"
pai.api_key.set("PAI-88646bdb-ec05-4bd5-bc9b-70ec3e5a05c7") 

df = pai.load("pai-personal-302e2/heart")

#etapp PAI-6f510483-9365-44c9-bfca-5eb3b0913323
#pai-personal-302e2/ gdc PAI-88646bdb-ec05-4bd5-bc9b-70ec3e5a05c7
