from enum import Enum, auto
from functools import reduce

from colorama import just_fix_windows_console, Fore, Style


def put(text):
    """Print a string without any appended newline

    :param text: The string to print
    :type text: str
    """
    print(text, end="")


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

    @classmethod
    def get(cls, field):
        """Retrieve a config value

        :param field: Value name
        :type field: str
        :return: The value of the config field
        :rtype: depends on the field
        """
        return cls._fields[field]

    @classmethod
    def set(cls, field, value):
        cls._fields[field] = value


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

        Follows the print_done_tasks config var to adjust returned contents.
        """
        if not self.done:
            return self.body

        print_type = Config.get("print_done_tasks")
        if print_type == "no":
            return ""
        elif print_type == "hidden":
            return "==="
        else:  # print_type == "yes"
            return self.body


class List:
    """An ordered, printable list of tasks

    Keep in mind that the tasks are printed starting from 1. When accessing
    tasks based on user input, you will need to subtract one.

    :param name: Name of the list
    :type name: str
    :param tasks: List of :class:`Task`s in the list. Can be freely manipulated
    :type tasks: list, optional
    """

    def __init__(self, name, tasks=None):
        """Constructor method
        """
        if tasks is None:
            tasks = []
        self.name = name
        self.tasks = tasks

    def __str__(self):
        """Print the list as numbered tasks, one per line

        Done tasks are greyed out.
        """
        result = ""
        for i in range(len(self.tasks)):
            task = self.tasks[i]
            if Config.get("print_done_tasks") == "no" and task.done:
                continue
            if not task.done:
                result += Fore.LIGHTWHITE_EX
            else:
                result += Fore.LIGHTBLACK_EX
            result += "#" + str(i + 1) + " " + str(task) + "\n"

        return result

    def count_done(self):
        """Count how many tasks are done

        :return: The number of tasks in the list that are done
        :rtype: int
        """
        return reduce(lambda acc, t: acc + 1 if t.done else acc, self.tasks, 0)


class TUI:
    """Runs the interactive terminal-based interface for the app
    """

    class State(Enum):
        NONE = 0  # Initial state
        HELP = auto()  # Help screen
        LIST_VIEW = auto()  # Displaying list overview
        SHUTDOWN = auto()  # Shutdown requested

    CONSOLE_SIZE = (80, 25)  # (w,h) column/row count

    state = State.NONE  # Current view of the global state machine
    last_result = "Welcome to Lists."  # Feedback from the most recent command
    lists = []  # All to-do lists owned by the user

    @classmethod
    def run(cls):
        """Initialize the terminal interface and run the main loop
        """
        # Initialize
        just_fix_windows_console()
        cls.state = cls.State.LIST_VIEW

        # Set up test content
        Config.set("print_done_tasks", "yes")
        cls.lists.append(List("Main"))
        test_list = cls.lists[0]
        test_list.tasks.append(Task("Hello world!"))
        test_list.tasks.append(Task("How are you?"))
        test_list.tasks.append(Task("I'm fine, thanks"))
        test_list.tasks.append(Task("The weather is horrible"))
        test_list.tasks.append(Task("It's freezing and wet"))
        test_list.tasks[0].done = True
        test_list.tasks[1].done = True
        test_list.tasks[2].done = True
        test_list.tasks[3].done = True
        test_list.tasks[4].done = True

        # Main loop
        while cls.state != cls.State.SHUTDOWN:
            cls._render()
            command = input("> ")
            cls._parse(command)

    @classmethod
    def _render(cls):
        """Redraw the screen contents
        """
        lines_printed = 0  #

        if cls.state == cls.State.HELP:
            pass

        elif cls.state == cls.State.LIST_VIEW:
            # Print the lists
            for i in range(len(cls.lists)):
                lst = cls.lists[i]
                idx = "#" + str(i)
                name = lst.name
                done_count = lst.count_done()
                task_count = len(lst.tasks)
                badge = "done!"
                if done_count < task_count:
                    badge = str(done_count) + "/" + str(task_count)
                put(idx + " " + name + " (" + badge + ")\n")
            lines_printed = len(cls.lists)

        # Print newlines until we're near the bottom
        put("\n" * (cls.CONSOLE_SIZE[1] - lines_printed - 2))

        # Print the result message
        put(cls.last_result + "\n")

    @classmethod
    def _parse(cls, cmd):
        """Parse a user-input command

        The input will be cleaned up, and the matching action will be executed.
        :param cmd: Command as input by the user
        :type cmd: str
        """
        # Sanitization
        cmd = cmd.strip()
        cmd = cmd.lower()

        if cmd == "exit":
            cls.state = cls.State.SHUTDOWN
        elif cmd == "help":
            cls.state = cls.State.HELP
            cls.last_result = "Help displayed. Input anything to return."
        elif cmd == "":
            cls.last_result = "Type \"help\" for assistance."
        else:
            cls.last_result = Fore.RED + "Unknown command." + Style.RESET_ALL


TUI.run()
