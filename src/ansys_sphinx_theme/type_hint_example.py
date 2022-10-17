"""Module containing an example function using type hinting."""
from typing import Union


def type_hint_func(param1: int = 1, param2: str = "test", param3: Union[int, float] = 1) -> bool:
    """Summary containing the function description.

    Extended description of the function. Can span multiple lines and
    provides a general overview of the function.

    Parameters
    ----------
    param1 :
        Description of an integer parameter.
    param2 :
        Description of a string parameter.
    param3 :
        Parameter that can be either int or float using Union (typing).

    Returns
    -------
    bool
        Description of the returned value.

    Examples
    --------
    >>> func(1, 'foo', 1)
    True

    """
    return True
