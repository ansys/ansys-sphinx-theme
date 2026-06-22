# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    >>> func(1, "foo", 1)
    True

    """
    return True
