# Pipelines

Pipelines provide a way to chain together multiple processing steps (called Building Blocks) for different tasks. They allow you to customize and reuse logic by composing reusable steps.

PandasAI provides some core building blocks for creating pipelines as well as some predefined pipelines for common tasks. Pipelines can also be fully customized by injecting custom logic at each step.

## Core Pipeline Building Blocks

PandasAI provides the following core pipeline logic units that can be composed to build custom pipelines:

- `Pipeline` - The base pipeline class that allows chaining multiple logic units.
- `BaseLogicUnit` - The base class that all pipeline logic units inherit from. Each unit performs a specific task.

## Predefined Pipelines

PandasAI provides the following predefined pipelines that combine logic units:

### GenerateSmartDataLakePipeline

The `GenerateSmartDataLakePipeline` generates new data in a SmartDatalake. It chains together logic units for:

- `CacheLookup` - Checking if data is cached
- `PromptGeneration` - Generating prompt
- `CodeGenerator` - Generating code from prompt
- `CachePopulation` - Caching generated data
- `CodeExecution` - Executing code
- `ResultValidation` - Validating execution result
- `ResultParsing` - Parsing result into data

### GenerateSDFPipeline

The `GenerateSDFPipeline` generates a new synthetic dataframe by chaining logic units:

- `SyntheticDataframePrompt` - Generating dataframe prompt
- `PromptExecution` - Executing prompt
- `SDFCodeExecutor` - Executing generated code
- `ProcessOutput` - Post-processing dataframe

## Custom Pipelines

Custom pipelines can be created by composing `BaseLogicUnit` implementations:

```python
class MyLogicUnit(BaseLogicUnit):
  def execute(self):
    ...

pipeline = Pipeline(
  units=[
     MyLogicUnit(),
     ...
  ]
)
```

This provides complete flexibility to inject custom logic.

## Extensibility

PandasAI pipelines are easily extensible via:

- Adding new logic units by sublassing `BaseLogicUnit`
- Creating new predefined pipelines by composing logic units
- Customizing behavior by injecting custom logic units

As PandasAI evolves, new logic units and pipelines can be added while maintaining a consistent underlying architecture.
