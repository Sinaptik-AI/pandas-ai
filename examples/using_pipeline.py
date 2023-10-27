import pandas as pd
from pandasai.llm.openai import OpenAI
from pandasai.pipelines.synthetic_dataframe.generate_sdf_pipeline import (
    GenerateSDFPipeline,
)
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.synthetic_dataframe.sdf_code_executor import (
    SDFCodeExecutor,
)
from pandasai.pipelines.synthetic_dataframe.synthetic_df_prompt import (
    SyntheticDataframePrompt,
)
from pandasai.pipelines.logic_units.prompt_execution import PromptExecution
from pandasai.pipelines.pipeline import Pipeline

employees_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Name": ["John", "Emma", "Liam", "Olivia", "William"],
        "Department": ["HR", "Sales", "IT", "Marketing", "Finance"],
    }
)

salaries_df = pd.DataFrame(
    {
        "EmployeeID": [1, 2, 3, 4, 5],
        "Salary": [5000, 6000, 4500, 7000, 5500],
    }
)

llm = OpenAI("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")

config = {"llm": llm, "verbose": True}

context = PipelineContext([salaries_df], config)

# Create your own pipeline
pipeline = Pipeline(
    config=config,
    context=context,
    steps=[SyntheticDataframePrompt(), PromptExecution(), SDFCodeExecutor()],
)

data_frame = pipeline.run()

print(data_frame)


# Using defined Pipelines
context = PipelineContext([employees_df], config)

pipeline = GenerateSDFPipeline(
    config={"llm": llm, "verbose": True},
    context=context,
)

data_frame = pipeline.run()

print(data_frame)
