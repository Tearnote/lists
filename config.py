class Config:
    """Facility for accessing global app configuration
    """

    class Field:
        """A single config field

        :param name: Identifier of the field, for use in code
        :type name: str
        :param value: The initial value of the field
        :type value: str
        :param description: Human-readable description of the field
        :type description: str
        :param values: A list of allowed values. If empty, any value is allowed
        :type values: list
        """

        def __init__(self, name, value, description, values=None):
            """Constructor method
            """
            self.name = name
            self.value = value
            self.description = description
            self.values = [] if values is None else values

    _fields = [
        Field("print_done_tasks",
              "hidden",
              "Show done tasks",
              ["yes", "no", "hidden"])
    ]

    @classmethod
    def get(cls, name):
        """Retrieve a config field's value

        :param name: Field name
        :type name: str
        :return: The value of the config field
        :rtype: str
        """
        return cls._find_field(name).value

    @classmethod
    def set(cls, name, value):
        """Set a config field to a provided value

        :param name: Field name
        :type name: str
        :param value: New value to set on the field
        :type value: str
        :raises ValueError: The provided value is invalid for the field
        """
        field = cls._find_field(name)
        if len(field.values) > 0 and field.values.count(value) == 0:
            raise ValueError
        field.value = value

    @classmethod
    def _find_field(cls, name):
        """Retrieve the field object with the given name

        :param name: Field name
        :type name: str
        :return: The field object
        :rtype: :class:`Field`
        """
        return next(filter(lambda f: f.name == name, cls._fields))
