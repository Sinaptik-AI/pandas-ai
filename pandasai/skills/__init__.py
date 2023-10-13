import inspect
import pandas as pd


# The @skill decorator to define and register a skill
def skill(name, description, usage):
    def decorator(skill_function):
        def wrapped_function(*args, **kwargs):
            return skill_function(*args, **kwargs)

        wrapped_function.skill_info = {
            "name": name,
            "description": description,
            "usage": usage,
        }
        wrapped_function.func_def = (
            """def pandasai.skill.{funcion_name}{signature}""".format(
                funcion_name=skill_function.__name__,
                signature=str(inspect.signature(skill_function)),
            )
        )

        return wrapped_function

    return decorator


@skill(
    name="Sales Forecast",
    description="Forecasts sales using time series models",
    usage="forecast sales for next month",
)
def forecast_sales(df: pd.DataFrame, query: str) -> str:
    print(df)
    print(query)
    return "Hello World!"
