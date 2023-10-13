import inspect
import pandas as pd

from pandasai.helpers.skills_manager import SkillsManager


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
        wrapped_function.print = (
            """
<function>
Name: {name}
Description: {description}
Usage: {usage}
{signature}
</function
"""
        ).format(
            name=name,
            description=description,
            usage=usage,
            signature=wrapped_function.func_def,
        )

        return wrapped_function

    return decorator
