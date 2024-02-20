import pandas as pd

from pandasai.llm.openai import OpenAI
from pandasai.pipelines.logic_units.output_logic_unit import ProcessOutput
from pandasai.pipelines.logic_units.prompt_execution import PromptExecution
from pandasai.pipelines.pipeline import Pipeline
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.synthetic_dataframe.generate_sdf_pipeline import (
    GenerateSDFPipeline,
)
from pandasai.pipelines.synthetic_dataframe.sdf_code_executor import (
    SDFCodeExecutor,
)
from pandasai.pipelines.synthetic_dataframe.synthetic_df_prompt import (
    SyntheticDataframePrompt,
)

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

llm = OpenAI("Your-API-Key")

config = {"llm": llm, "verbose": True}

context = PipelineContext([salaries_df], config)

# Create your own pipeline
pipeline = Pipeline(
    context=context,
    steps=[
        SyntheticDataframePrompt(amount=15),
        PromptExecution(),
        SDFCodeExecutor(),
        ProcessOutput(),
    ],
)

data_frame = pipeline.run()

print(data_frame)


# Using defined Pipelines
context = PipelineContext([employees_df], config)

pipeline = GenerateSDFPipeline(
    amount=10,
    context=context,
)

data_frame = pipeline.run()

print(data_frame)


# Without passing Context
pipeline = Pipeline(
    [salaries_df],
    config=config,
    steps=[
        SyntheticDataframePrompt(amount=15),
        PromptExecution(),
        SDFCodeExecutor(),
        ProcessOutput(),
    ],
)

data_frame = pipeline.run()

print(data_frame)
