"""Validator tests.

This module contains unit tests for Flask-Neo4jDriver Validators.

"""
import pytest
import sys
from faker import Faker
from flask_neo4j.validator import (Validator, Integer, String)

fake = Faker()
try:  # Python 2
    sys.maxint
    intmax = sys.maxint
    intmin = -sys.maxint - 1
except AttributeError:  # Python 3
    intmax = sys.maxsize
    intmin = -sys.maxsize - 1

pytestmark = pytest.mark.validators


@pytest.fixture
def validator():
    class TestClass(object):
        x = Validator()
    return TestClass()


def test_validator_base_attributes():
    """Test attributes of the base validator."""
    v = Validator()
    assert v.name is None


def test_validator_init_assignment():
    """Test attributes can be assigned at creation."""
    v = Validator(name="test")
    assert v.name == "test"


def test_validator_get_method(validator):
    """Test validator `__get__` returns attribute or raises exception."""
    with pytest.raises(KeyError):
        validator.x


def test_validator_validate_method_is_abstract():
    """Test that `validate()` does not have an implementation."""
    v = Validator()
    with pytest.raises(NotImplementedError):
        v.validate(20)


def test_validator_set_calls_validate_method(validator):
    """Test that `__set__` calls the `validate` method."""
    with pytest.raises(NotImplementedError):
        validator.x = 20


def test_default_integer_init_values():
    """Test Integer() validator has success with an integer."""
    v = Integer()
    assert v.name is None
    assert v.positive is False


def test_integer_init_value_assignment():
    """Test Integer() can be passed values at creation."""
    v = Integer(name='test', positive=True)
    assert v.name == 'test'
    assert v.positive is True


@pytest.mark.parametrize("value", [0, 1, -2, intmax, intmin])
def test_integer_accepts_integers(value):
    """Test Integer() validator accepts valid integers."""
    v = Integer()
    v.validate(value)


@pytest.mark.parametrize("value", ['0', 0.1, float('inf')])
def test_integer_raises_exception_if_invalid_integer(value):
    """Test that Integers `validate` throws exception if not an int."""
    with pytest.raises(TypeError) as err:
        v = Integer()
        v.validate(value)
    assert 'to be an integer; got' in str(err.value)


def test_integer_positive_validation():
    """Test that `positive` flag throws exception if int is negative."""
    v = Integer(positive=True)
    with pytest.raises(TypeError) as err:
        v.validate(-1)
    assert 'not a positive integer' in str(err.value)


def test_string_default_init_values():
    """Test default value assignent for String validator."""
    s = String()
    assert s.name is None
    assert s.max_length is None
    assert s.min_length is None


def test_string_default_init_value_assignment():
    """Test `String` can be assigned values at instantiation."""
    s = String(name='test', max_length=1, min_length=1)
    assert s.name == 'test'
    assert s.max_length == 1
    assert s.min_length == 1


def test_string__max_length_attributes_must_be_integers():
    """Test that a `String` validators length attributes must be an integer."""
    with pytest.raises(TypeError) as err:
        String(max_length='1')
    assert 'max_length must be an integer' in str(err.value)


def test_string__min_length_attributes_must_be_integers():
    """Test that a `String` validators length attributes must be an integer."""
    with pytest.raises(TypeError) as err:
        String(min_length='1')
    assert 'min_length must be an integer' in str(err.value)


def test_string_accepts_valid_strings():
    """Test the `String` validator accepts valid strings."""
    s = String()
    s.validate('')
    for _ in range(50):
        s = String()
        s.validate(fake.text())


@pytest.mark.parametrize("locale", [
    'ar_SA',
    'el_GR',
    'fa_IR',
    'hi_IN',
    'ja_JP',
    'ko_KR',
    'zh_CN',
    'zh_TW'
], ids=[
    'Arabic',
    'Greek',
    'Persian',
    'Hindi',
    'Japanese',
    'Korean',
    'Chinese',
    'Taiwan']
)
def test_string_accepts_unicode_strings(locale):
    """Test that the `String` validator accepts valid unicode strings."""
    for _ in range(50):
        s = String()
        f = Faker(locale)
        s.validate(f.text())


def test_string_raises_exception_if_not_string():
    """Test that `String` throws an exception if type is not string."""
    with pytest.raises(TypeError) as err:
        s = String()
        s.validate(0)
    assert 'Expected 0 to be a string; got int instead' in str(err.value)


def test_string_raises_exception_if_max_length_violation():
    """Test that `String` throws an exception if max_length violation."""
    s = String(max_length=2)
    s.validate('a')   # No Exception
    s.validate('aa')  # No Exception
    with pytest.raises(TypeError) as err:
        s.validate('aaa')
    assert 'is longer than max length 2' in str(err.value)


def test_string_raises_exception_if_min_length_violation():
    """Test that `String` throws an exception if min_length violation."""
    s = String(min_length=2)
    s.validate('aa')  # No Exception
    with pytest.raises(TypeError) as err:
        s.validate('a')
    assert 'is shorter than min length 2' in str(err.value)


def test_string_validator_set_hook():
    """Test that `String` intercepts `__set__` to call `validate`"""
    class MyTest(object):
        test = String()
    t = MyTest()
    t.test = 'testing'
    with pytest.raises(TypeError) as err:
        t.test = 1
    assert 'Expected 1 to be a string; got int instead' in str(err.value)
