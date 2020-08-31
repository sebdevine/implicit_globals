# noinspection PyPackageRequirements
import pytest
from implicit_globals import ImplicitGlobals


AAA = "FRE"


def load():
    return "Hello"


def foo(a, b, c=1, *, d=None):
    return "foo", a, b, c, d, AAA, load()


def bar(a, b):
    return a + b, foo(a, b)


def test_implicit_one_func():
    implicit = ImplicitGlobals()
    assert foo(3, 4) == ("foo", 3, 4, 1, None, "FRE", "Hello")
    foo2 = implicit(foo)
    assert foo2(3, 4) == ("foo", 3, 4, 1, None, "FRE", "Hello")
    implicit['AAA'] = 'BAR'
    assert foo2(3, 4) == ("foo", 3, 4, 1, None, "BAR", "Hello")
    # No side effect
    assert foo(3, 4) == ("foo", 3, 4, 1, None, "FRE", "Hello")
    implicit["load"] = lambda: "New Hello"
    assert foo2(3, 4) == ("foo", 3, 4, 1, None, "BAR", "New Hello")
    assert foo(3, 4) == ("foo", 3, 4, 1, None, "FRE", "Hello")
    implicit["d"] = 333
    assert foo2(3, 4) == ("foo", 3, 4, 1, 333, "BAR", "New Hello")
    assert foo(3, 4) == ("foo", 3, 4, 1, None, "FRE", "Hello")
    implicit["b"] = 789789
    assert foo2(3, 4) == ("foo", 3, 4, 1, 333, "BAR", "New Hello")
    assert foo(3, 4) == ("foo", 3, 4, 1, None, "FRE", "Hello")
    del implicit["AAA"]
    assert foo2(3, 4) == ("foo", 3, 4, 1, 333, "FRE", "New Hello")
    del implicit["load"]
    assert foo2(3, 4) == ("foo", 3, 4, 1, 333, "FRE", "Hello")
    del implicit["d"]
    assert foo2(3, 4) == ("foo", 3, 4, 1, None, "FRE", "Hello")
    assert len(implicit) == 1
    assert "b" in implicit
    assert list(iter(implicit)) == ["b"]


def test_implicit_two_funcs():
    implicit = ImplicitGlobals()
    assert bar(8, 9) == (17, ("foo", 8, 9, 1, None, "FRE", "Hello"))
    foo2 = implicit(foo)
    bar2 = implicit(bar)
    assert bar2(8, 9) == (17, ("foo", 8, 9, 1, None, "FRE", "Hello"))
    implicit['AAA'] = 'BAR'
    assert bar2(8, 9) == (17, ("foo", 8, 9, 1, None, "FRE", "Hello"))
    implicit['foo'] = foo2
    assert bar2(8, 9) == (17, ("foo", 8, 9, 1, None, "BAR", "Hello"))
    assert bar(8, 9) == (17, ("foo", 8, 9, 1, None, "FRE", "Hello"))
    implicit["load"] = lambda: "New Hello"
    assert bar2(8, 9) == (17, ("foo", 8, 9, 1, None, "BAR", "New Hello"))
    assert bar(8, 9) == (17, ("foo", 8, 9, 1, None, "FRE", "Hello"))
    implicit["d"] = 333
    assert bar2(8, 9) == (17, ("foo", 8, 9, 1, 333, "BAR", "New Hello"))
    assert bar(8, 9) == (17, ("foo", 8, 9, 1, None, "FRE", "Hello"))
    implicit["b"] = 789789
    assert bar2(8, 9) == (17, ("foo", 8, 9, 1, 333, "BAR", "New Hello"))
    assert bar(8, 9) == (17, ("foo", 8, 9, 1, None, "FRE", "Hello"))


def test_implicit_method():
    implicit = ImplicitGlobals()

    class Baz:

        @implicit
        def method(self, a, b):
            return a + b, foo(a, b)

    baz = Baz()
    assert baz.method(10, 4) == (14, ("foo", 10, 4, 1, None, "FRE", "Hello"))
    foo2 = implicit(foo)
    implicit['foo'] = foo2
    assert baz.method(10, 4) == (14, ("foo", 10, 4, 1, None, "FRE", "Hello"))
    implicit['AAA'] = 'BAR'
    assert baz.method(10, 4) == (14, ("foo", 10, 4, 1, None, "BAR", "Hello"))
    implicit["load"] = lambda: "New Hello"
    assert baz.method(10, 4) == (14, ("foo", 10, 4, 1, None, "BAR", "New Hello"))
    implicit["d"] = 333
    assert baz.method(10, 4) == (14, ("foo", 10, 4, 1, 333, "BAR", "New Hello"))
    implicit["b"] = 789789
    assert baz.method(10, 4) == (14, ("foo", 10, 4, 1, 333, "BAR", "New Hello"))


def test_errors():
    implicit = ImplicitGlobals()

    with pytest.raises(TypeError):
        implicit(lambda: None)

    with pytest.raises(TypeError):
        implicit(333)
