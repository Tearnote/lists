from colorama import Fore, Style


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

        def set(self, value):
            """Sets the field to provided value, with validity checking

            :param value: New value to set
            :type value: str
            :raises ValueError: Value is not valid
            """
            if len(self.values) > 0 and self.values.count(value) == 0:
                raise ValueError(
                    f"\"{value}\""
                    f" is not an allowed value for "
                    f"\"{self.description}\".")

            self.value = value

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
        :raises ValueError: No field with such name
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
        :raises ValueError: No field with such name, or the provided value
        is invalid for the field
        """
        cls._find_field(name).set(value)

    @classmethod
    def set_at(cls, index, value):
        """Set a config field by index

        The index corresponds to numbers as shown in the print() output,
        and is typically user-provided.

        :param index: Field index
        :type index: int
        :param value: New value to set on the field
        :type value: str
        :raises IndexError: The provided index is out of range
        :raises ValueError: The provided value is invalid for the field
        """
        try:
            cls._fields[index - 1].set(value)
        except IndexError:
            raise IndexError(f"There is no field with index {index}.")

    @classmethod
    def description_at(cls, index):
        """Return the description of the field at the provided index

        :param index: Field index
        :type index: int
        :raises IndexError: The provided index is out of range
        :return: The config field's description
        :rtype: str
        """
        index -= 1
        return cls._fields[index].description

    @classmethod
    def _find_field(cls, name):
        """Retrieve the field object with the given name

        :param name: Field name
        :type name: str
        :raises ValueError: Field was not found
        :return: The field object
        :rtype: :class:`Field`
        """
        try:
            return next(filter(lambda f: f.name == name, cls._fields))
        except StopIteration:
            raise ValueError(f"There is no config field called \"{name}\"")

    @classmethod
    def print(cls):
        """Return the string with the human-readable state of all fields

        :return: String with one field per line
        :rtype: str
        """
        result = ""
        for i in range(len(cls._fields)):
            field = cls._fields[i]
            index = i + 1
            values_text = ""
            if len(field.values) > 0:
                values_text += f" {Fore.LIGHTBLACK_EX}["
                values_text += ", ".join(field.values)
                values_text += f"]{Style.RESET_ALL}"
            value = f"{Fore.GREEN}{field.value}{Style.RESET_ALL}"
            result += f"#{index} {field.description}: {value}"
            result += f"{values_text}\n"
        return result
