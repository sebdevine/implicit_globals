# -*- coding: utf-8 -*-
# module implicit_globals.py
#
# Copyright (c) 2020 Sebastien Devine
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
__version__ = "1.0.0"
__author__ = "Sebastien Devine"
__email__ = "sebdevine@users.noreply.github.com"
__github__ = "https://github.com/sebdevine/implicit_globals"

__doc__ = """A decorator that provides a way to override a function's global variables

Those global/default variables can be overriden using a dict-like api.

Notes:
    - Inspired from Scala's implicits
    - Chain functions and manage interwined function with global
      / default variables hanging around
    - Another way to monkey patch with an explicit mechanism to override
    - Easy for non-experts to just import and decorate functions/methods

Warnings:
    - NO thread-safety
    - NO async/coroutine support (yet)
    - You must instanciate another `Implicit` decorator if you want
      to keep things separate (per class / module etc)

Usage:
    You can use either the default decorator, or instanciate you own

    >>> import sys
    >>> from implicit_globals import implicit
    >>>
    >>> AAA = "FRE"
    >>>
    >>> def load():
    ...     return "Hello"
    >>>
    >>> @implicit
    >>> def foo(a, b, c=1, *, d=None):
    ...     print("foo : ", a, b, c, d, AAA, load())

    >>> foo(3, 4)
    foo :  3 4 1 None FRE Hello

    >>> # Override a global variable
    >>> implicit["AAA"] = "BAZ"
    >>> # Override builtin function
    >>> implicit["print"] = \
    ...     lambda *_: sys.stdout.write("YO-- %s\\n" % ', '.join(map(str, _)))
    >>> # Override global function
    >>> implicit["load"] = lambda: "New Hello"
    >>> # Override default parameter
    >>> implicit["d"] = 333

    >>> foo(3, 4)
    YO-- foo : , 7, 8, 1, 333, BAZ, New Hello

    Function can also be changed, with above definitions :
    >>> @implicit
    >>> def bar(a, b):
    ...     print("bar : ", a, b, AAA)
    ...     foo(a, b)

    >>> bar(3, 4)
    YO-- bar : , 3, 4, BAZ
    YO-- foo : , 3, 4, 1, 333, BAZ, New Hello
"""

import copy
import functools
import inspect
import types
from typing import MutableMapping

__all__ = ["ImplicitGlobals", "implicit"]


def islambda(func: callable) -> bool:
    def lmb():
        return lambda: None

    return isinstance(func, type(lmb())) and func.__name__ == lmb().__name__


class ImplicitGlobals(MutableMapping):
    """Dict-like object that stores global variables, its instances can be used as decorators
    """

    def __init__(self, **overrides):
        self._overrides = overrides

    def __len__(self):
        return len(self._overrides)

    def __iter__(self):
        return iter(self._overrides)

    def __delitem__(self, key):
        del self._overrides[key]

    def __getitem__(self, item):
        return self._overrides[item]

    def __setitem__(self, key, value):
        self._overrides[key] = value

    # noinspection PyMethodParameters
    def __call__(this, func: callable) -> callable:
        """Called upon function decoration
        """
        if not inspect.isfunction(func):
            raise TypeError("Expecting a function, got: " + type(func).__name__)

        if islambda(func):
            raise TypeError("Cannot work on lambda functions")

        is_method = inspect.ismethod(func)

        def new_func() -> types.FunctionType:
            __globals__: dict = dict(func.__globals__)
            __globals__.update(this._overrides)

            # noinspection PyTypeChecker
            new_f: types.FunctionType = functools.update_wrapper(
                wrapped=func,
                wrapper=types.FunctionType(
                    func.__code__,
                    __globals__,
                    name=func.__name__,
                    argdefs=func.__defaults__,
                    closure=func.__closure__,
                ),
            )

            # Reconstruct the keyword arguments' defaults
            fa: inspect.FullArgSpec = inspect.getfullargspec(func)
            func_args = fa.args or tuple()
            func_defaults = fa.defaults or tuple()
            func_kwdefaults = fa.kwonlydefaults or dict()

            __kwdefaults__ = dict(
                zip(func_args[::-1], func_defaults[::-1],), **func_kwdefaults
            )
            for k, v in __kwdefaults__.items():
                if k in this._overrides:
                    __kwdefaults__[k] = this._overrides[k]

            new_f.__kwdefaults__ = __kwdefaults__
            return new_f

        if not is_method:
            # Pure function
            def wrapper(*args, **kwargs):
                return new_func()(*args, **kwargs)

        else:
            # Method => must have self as first argument
            def wrapper(self, *args, **kwargs):
                return new_func()(self, *args, **kwargs)

        functools.update_wrapper(wrapped=func, wrapper=wrapper)
        return wrapper


#: Default globals implicits decorator
implicit = ImplicitGlobals()
