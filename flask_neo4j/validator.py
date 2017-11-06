"""Model Validators

This module contains a set of default validators that can be used to richly
express attributes on application models.

"""
import uuid


class Validator(object):
    """Base Validator.

    Resource Types such as :class:`Node` or :class:`Relationship` can use
    :class:`Validators` to ensure attributes meet certain criteria. Validators
    should inherit from this class and implement the `validate` method.

    Example usage::

        class Integer(Validator):
            def validate(value):
                if not isinstance(value, int):
                    raise TypeError('expected an int')

        class MyModel(Node):
            price = Integer()  # ensure MyModel.price is an int

    """
    def __init__(self, name=None):
        """Initialize a new validator.

        Args:
            :param name: The name of the attribute to be validated. This is
                typically None as the resource class will discover this at
                runtime.

        """
        self.name = name

    def __get__(self, instance, cls):
        """Return the attribute is it exists.

        Raises:
            TypeError: if `self.name` does not exist as an attribute.

        """
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        """Intercept the dot on setting an attribute.

        Override set to validate the value of an attribute before setting it.

        """
        self.validate(value)
        instance.__dict__[self.name] = value

    def validate(self, value):
        """Abstract method.

        Children need to implement this method to validate `value`.  This
        method should raise an exception if the value does not pass validation.

        """
        raise NotImplementedError(
            'validate() needs a concrete implementation.')


class Integer(Validator):
    """Integer validator.

    Assert the passed value is an integer and optionally a positive integer.

    """
    def __init__(self, name=None, positive=False):
        """Initialize the validator.

        Args:
            :param name: Name of the attribute; see :class:`Validator`
            :param positive: Flag to determine if the integer must be positive.

        """
        self.name = name
        self.positive = positive
        super().__init__(name)

    def validate(self, value):
        """Validate the attribute meets the configured criteria."""
        if not isinstance(value, int):
            raise TypeError(
                "Expected '{}' to be an integer; got {} instead.".format(
                    value, value.__class__.__name__))
        if self.positive:
                if value < 0:
                    raise TypeError(
                        '{} is not a positive integer'.format(value))


class String(Validator):
    """String validator.

    Assert the passed value is a string and meets configured requirements.

    """
    def __init__(self, name=None, max_length=None, min_length=None):
        """Initialize the validator.

        Args:
            :param name: Name of the attribute; see :class:`Validator`
            :param max_length: integer representing the max length of the str

        """
        self.name = name
        if max_length:
            if not isinstance(max_length, int):
                raise TypeError('max_length must be an integer.')

        if min_length:
            if not isinstance(min_length, int):
                raise TypeError('min_length must be an integer.')

        self.max_length = max_length
        self.min_length = min_length
        super().__init__(name)

    def validate(self, value):
        """Validate `value` is a string.

        This validator validates the attribute is a type of string and
        optionally that the string falls within a certain length range.

        """
        if not isinstance(value, str):
            raise TypeError(
                "Expected {} to be a string; got {} instead.".format(
                    value, value.__class__.__name__))

        length = len(value)
        if self.max_length:
            if length > self.max_length:
                raise TypeError(
                    "'{}' ({}) is longer than max length {}".format(
                        value, length, self.max_length))
        if self.min_length:
            if length < self.min_length:
                raise TypeError(
                    "'{}' ({}) is shorter than min length {}".format(
                        value, length, self.min_length))


class Float(Validator):
    """Float Validator.

    Assert the attributes assigned a floating point number. Optionally test for
    a positive floating point value.

    """

    def __init__(self, name=None, positive=False):
        """Initialize the validator.

        Args:
            :param name: Name of the attribute; see :class:`Validator`
            :param positive: Flag to determine if the float must be positive.

        """
        self.name = name
        self.positive = positive
        super().__init__(name)

    def validate(self, value):
        """Validate that `value` is a floating point number."""
        if not isinstance(value, float):
            raise TypeError(
                'Expected {} to be a float; got {} instead.'.format(
                    value, value.__class__.__name__))

        if self.positive:
            if value < 0:
                raise TypeError(
                   'Expected {} to be positive.'.format(value))


class UUID(Validator):
    """UUID Validator.

    The UUID validator is a special validator.  The UUID validator operates as
    as UUID generator.  When this validator is used it ensures a unique UUID
    is returned.  If the validator is not provided a function to generate a
    unique identified, then `uuid.uuid4()` will be used.

    Example::
        class MyModel(object):
            uid = UUID(func=uuid.uuid4)

        obj = MyModel()
        print(f'obj.uid')  # returns a unique id
        print(f'obj.uid')  # returns the same identified
        obj.uid = '123'    # overwrites the uid with a custom value

    """
    def __init__(self, name=None, func=lambda: str(uuid.uuid4())):
        """Initialize the validator.

        note: This validator does no type conversion on the return value from
        the `func` function.

        Args:
            :param name: Name of the attribute; see :class:`Validator`
            :param funct: Function to generate a unique identifier

        """
        self.name = name
        self.func = func

    def __get__(self, instance, cls):
        """Override `Validator.__get__`

        Returns the value stored in the attribute if it exists; otherwise a
        new unique identifier is generated, stored, and then returned.

        """
        try:
            return instance.__dict__[self.name]
        except KeyError:
            instance.__dict__[self.name] = self.func()
        return instance.__dict__[self.name]

    def validate(self, value):
        pass
