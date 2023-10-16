import inspect


# The @skill decorator to define and register a skill
def skill(name: str, description: str, usage: str):
    def decorator(skill_function):
        def wrapped_function(*args, **kwargs):
            return skill_function(*args, **kwargs)

        wrapped_function.name = skill_function.__name__
        wrapped_function.skill_info = {
            "name": name,
            "description": description,
            "usage": usage,
        }
        wrapped_function.func_def = (
            """def pandasai.skills.{funcion_name}{signature}""".format(
                funcion_name=wrapped_function.name,
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
