import inspect


def skill(skill_function):
    def wrapped_function(*args, **kwargs):
        return skill_function(*args, **kwargs)

    wrapped_function.name = skill_function.__name__
    wrapped_function.func_def = (
        """def pandasai.skills.{funcion_name}{signature}""".format(
            funcion_name=wrapped_function.name,
            signature=str(inspect.signature(skill_function)),
        )
    )

    doc_string = skill_function.__doc__

    wrapped_function.print = (
        """
<function>
{signature}
{doc_string}
</function>
"""
    ).format(
        signature=wrapped_function.func_def,
        doc_string="""    \"\"\"{0}\n    \"\"\"""".format(doc_string)
        if doc_string is not None
        else "",
    )

    return wrapped_function
