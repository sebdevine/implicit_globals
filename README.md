# implicit-globals
![](https://api.travis-ci.com/sebdevine/implicit_globals.svg?branch=master&status=passed)

**TL;DR: A Python decorator that allow you to modify at runtime a function's 
implicit global variables or default variables.**

## Goals
The _implicit_ adjective refers to all variables that are not explicit to a function call,
either from the function (or method) 's global variables or any parameter with a default value.
It is heavily inspired from Scala's own implicit types, but obviously not the same, Scala solves implicitly at compile time.

Using "pure" functions is not always possible, using an external variable/function is
quite easy in Python, but then when it comes to changing those dependencies, it is quite difficult:
think about testing, dependency injection, etc. So people often resort to "objects" as an easy way to override things, class attributes/methods replace global variables/functions. This way can make the code quite complex as `self` becomes the global repository with overrides all over the place.

The idea is to keep some sort of "functional approach" but keep things manageable with an explicit "global' memory" that manipulates global variables without changing the function's call graph.
And also without resorting on the "heavy artillery" of functional programming patterns.

The main issue of this approach is to know in advance which are the global variables used and their
type. Obviously Python duck typing makes things easier, but still we cannot statically know
the dependencies in advances, so there is no check and control over the overrides.

## Install
```
pip install implicit-globals
```

## Usage

You can use either :
- The default decorator `implicit`, **but beware, then all functions 
decorated will share the same overrides !** 
- Or you can create your own local decorator using the class `ImplicitGlobals` : `my_implicit_decorator = ImplicitGlobals()`

The instances of `ImplicitGlobals` act like a mutable `dict` where the global names and their values can be set. 

Please note that :
- It is developed & tested on Python 3.6+, no older versions support.
- It is not thread-safe (concurent changes can lead to unexpect behaviour)
- It does not support (yet) coroutines
- Only decorated functions can be changed, others are left untouched.  

```python
import sys
#Use the default decorator
from implicit_globals import implicit


AAA = "FRE"


def load():
    return "Hello"


@implicit
def foo(a, b, c=1, *, d=None):
    print("foo : ", a, b, c, d, AAA, load())


@implicit
def bar(a, b):
    print("bar : ", a, b, AAA)
    foo(a, b)


@implicit
def qux(a, b=4):
    print("qux : ", a, b, AAA)
    bar(a, b)


class Foo:

    @implicit
    def toto(self, a, b):
        print('TOTO: ', a, b)
        bar(a, b)


qux(3, 4)
# qux :  3 4 FRE
# bar :  3 4 FRE
# foo :  3 4 1 None FRE Hello

implicit["AAA"] = "BAZ"
implicit["print"] = lambda *_: sys.stdout.write("YO-- " + ', '.join(map(str, _)) + '\n')
implicit["load"] = lambda: "New Hello"
implicit["d"] = 333

qux(3, 4)
# YO-- qux : , 3, 4, BAZ
# YO-- bar : , 3, 4, BAZ
# YO-- foo : , 3, 4, 1, 333, BAZ, New Hello

Foo().toto(7, 8)
# YO-- TOTO: , 7, 8
# YO-- bar : , 7, 8, BAZ
# YO-- foo : , 7, 8, 1, 333, BAZ, New Hello

del implicit["AAA"]
foo(4, 5)
# YO-- foo : , 4, 5, 1, 333, FRE, New Hello
```

## Development / Testing
To install local a development version :
```
pip install -e .
```

To launch the tests, you will need `pytest` :
```
pytest test_implicit_globals.py
```

To build and deploy, you will need these packages : `wheel`, `twine`, `setuptools`
```
python setup.py bdist_wheel
python -m twine upload --repository pypi dist/*
```
