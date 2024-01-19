from pandasai.pipelines.base_logic_unit import BaseLogicUnit
from pandasai.pipelines.pipeline_context import PipelineContext
from pandasai.pipelines.pipeline import Pipeline

# Create your own pipeline
context = PipelineContext([])


class GenerateCode(BaseLogicUnit):
    def execute(self, input, print_message="Hello World"):
        return f"print('{print_message}')"


class CodeExecutor(BaseLogicUnit):
    def execute(self, input, **kwargs):
        exec(input)


pipeline = Pipeline(
    context=context,
    steps=[
        GenerateCode(print_message="Hello World"),
        CodeExecutor(),
    ],
)

# This will print "Hello World"
data_frame = pipeline.run()
