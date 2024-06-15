import os
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from pandasai.agent import Agent
from deepeval.dataset import EvaluationDataset
from .tests import tests as benchmark

os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

test_cases = []
answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.8)
for test in benchmark:
    query = test["input"]
    expected_output = test["expected_output"]

    agent = Agent(
        test["datasets"],
        config={"enable_cache": True, "open_charts": False},
    )
    agent.chat(query)

    test_case = LLMTestCase(
        input=query,
        context=["Generate the code to answer the question."],
        expected_output=expected_output,
        actual_output=agent.last_code_executed,
    )
    test_cases.append(test_case)

evaluation_dataset = EvaluationDataset(test_cases)
evaluation_dataset.evaluate([answer_relevancy_metric])
