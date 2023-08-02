from unittest.mock import patch
from pandasai.llm.poe_api import POEAPI


class TestPOEAPI(unittest.TestCase):
    """Unit tests for the base GPT4All LLM class"""

    def setUp(self):
        self.bot_name = "chinchilla"
        self.token = ''
        
        self.poe_api_bot = POEAPI(
            model_name=self.model_name,
        )

    def test_type(self, ):
        
        assert self.poe_api_bot.type == "POEAPI"