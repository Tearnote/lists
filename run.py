from colorama import just_fix_windows_console, Fore, Style


class Config:
    """Facility for accessing global app configuration
    """

    _fields = {
        # How to print tasks that are marked done
        # "yes": Print the full text
        # "hidden": Print replacement text
        # "no": Skip printing the task entirely
        "print_done_tasks": "hidden"
    }

    @staticmethod
    def get(field):
        """Retrieve a config value

        :param field: Value name
        :type field: str
        :return: The value of the config field
        :rtype: depends on the field
        """
        return Config._fields[field]

    @staticmethod
    def set(field, value):
        Config._fields[field] = value


class Task:
    """A single entry of a to-do list

    :param body: Body text of the task
    :type body: str
    :param done: `True` if the task is marked as completed, defaults to `False`
    :type done: bool, optional
    """

    def __init__(self, body, done=False):
        """Constructor method
        """
        self.body = body
        self.done = done

    def __str__(self):
        """Make tasks printable

        Inserts ANSI color, and follows the print_done_tasks config var
        """
        if not self.done:
            return self.body

        print_type = Config.get("print_done_tasks")
        if print_type == "no":
            return ""
        elif print_type == "hidden":
            return Fore.LIGHTBLACK_EX + "==="
        else:  # print_type == "yes"
            return Fore.LIGHTBLACK_EX + self.body


just_fix_windows_console()

task = Task("Hello World!")
print(task)
task.done = True
Config.set("print_done_tasks", "yes")
print(task)
Config.set("print_done_tasks", "hidden")
print(task)
Config.set("print_done_tasks", "no")
print(task)
