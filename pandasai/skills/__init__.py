from abc import abstractmethod

from pydantic import BaseModel, PrivateAttr
from typing import Callable, Any, Optional
import inspect


class Skill(BaseModel):
    """Skill that takes a function usable by pandasai"""

    func: Callable[..., Any]
    description: Optional[str] = None
    _name: Optional[str] = PrivateAttr()
    _signature: Optional[str] = PrivateAttr()

    def __call__(self, *args, **kwargs) -> Any:
        if not self.func:
            raise ValueError("Must provide a function to this skill.")
        return self.func(*args, **kwargs)

    @classmethod
    def from_function(
        cls,
        func: Callable,
        description: Optional[str] = None,
    ) -> "Skill":
        """
        Creates a skill object from a function

        Args:
            func: The function from which to create a skill
            description: The description of the skill. Defaults to the function docstring.

        Returns:
            the `Skill` object

        """
        name = func.__name__
        sig = str(inspect.signature(func))
        signature = """def {function_name}{signature}:""".format(
            function_name=name,
            signature=sig,
        )

        description = description or func.__doc__
        if description is None:
            # if description is None then the function doesn't have a docstring
            # and the user didn't provide any description
            raise ValueError(
                f"Function must have a docstring if no description is provided for skill {name}."
            )
        cls._signature = signature
        cls._name = name

        return cls(description=description, func=func)

    def __str__(self):
        return f"""
<function>
{self._signature}
    \"\"\"{self.description}\"\"\"
</function>"""

    @property
    def name(self) -> str:
        return self._name


def skill(*args: Callable) -> Callable:
    """Decorator to create a skill out of functions
    Must be used without arguments. The function must have a docstring.

    Args:
        *args: The arguments to the skill

    Examples:
        .. code-block:: python

            @skill
            def compute_flight_prices(offers: pd.Dataframe) -> List[float]:
                # Computes the flight prices
                return
    """

    def _make_skill(skill_fn: Callable) -> Skill:
        return Skill.from_function(
            # when this decorator is used, the function MUST have a docstring
            description=skill_fn.__doc__,
            func=skill_fn,
        )

    if len(args) == 1 and callable(args[0]):
        return _make_skill(args[0])
    else:
        raise ValueError("Too many arguments for skill decorator")
