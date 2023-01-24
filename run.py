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


class UserInput:
    """Parsed representation of a user input

    :param keyword: The command the user is invoking
    :type keyword: str
    :param args: All text after the keyword
    :type args: str
    :param index_arg: Index part of args, if present
    :type index_arg: str
    :param text_arg: All text after index_arg, if present
    :type text_arg: str
    """

    def __init__(self, keyword, args, index_arg, text_arg):
        self.keyword = keyword
        self.args = args
        self.index_arg = index_arg
        self.text_arg = text_arg

    @classmethod
    def parse(cls, cmd):
        """Parse a string input by the user into a clean command input

        :param cmd: Full string of text entered by the user
        :type cmd: str
        """
        cmd = cmd.lower().strip()
        keyword, _, args = cmd.partition(" ")
        args = args.strip()
        index_arg, _, text_arg = args.partition(" ")
        text_arg = text_arg.strip()
        return cls(keyword, args, index_arg, text_arg)


class Command:
    """A user command, which might accept arguments and runs provided code

    :param keyword: Name of the command
    :type keyword: str
    :param callback: Code to run on command execution
    :type callback: function
    :param has_index_arg: Whether the command accepts an index argument
    :type has_index_arg: bool, optional
    :param index_arg_required: If `has_index_arg` is True, whether the command
    requires the index argument
    :type index_arg_required: bool, optional
    :param has_text_arg: Whether the command accepts a string argument
    :type has_text_arg: bool, optional
    :param text_arg_required: If `has_text_arg` is True, whether the command
    requires the string argument
    :type text_arg_required: bool, optional
    """

    def __init__(self, keyword, callback,
                 has_index_arg=False, index_arg_required=False,
                 has_text_arg=False, text_arg_required=False):
        """Constructor method
        """
        self.keyword = keyword
        self.callback = callback
        self.has_index_arg = has_index_arg
        self.index_arg_required = index_arg_required
        self.has_text_arg = has_text_arg
        self.text_arg_required = text_arg_required


class TUI:
    """Runs the interactive terminal-based interface for the app
    """

    class State(Enum):
        """Symbols representing possible states of the UI
        """
        NONE = 0  # Initial state
        HELP = auto()  # Help screen
        LIST_VIEW = auto()  # Displaying list overview
        SHUTDOWN = auto()  # Shutdown requested

    CONSOLE_SIZE = (80, 25)  # (w,h) column/row count
    HELP_TEXT = [
        "Lists is controlled with text commands. You can see the list of",
        "available commands in the pane on the right.",
        "",
        "The symbol \"#\" refers to an item index, for example the number",
        "of a list or a task. You can see the index next to each item",
        "on the main screen, for example:",
        "",
        f"#{Fore.GREEN}2{Style.RESET_ALL} Wash the dishes",
        "",
        "The symbol \"...\" stands for any text of your choice, like the full",
        "description of a new task. Surrounding the text in quotes",
        "is not required.",
        "",
        "You can also receive help on a specific command, as long as it's",
        "available from the current screen:",
        "",
        f"help {Fore.GREEN}delete{Style.RESET_ALL}",
    ]

    state = State.NONE  # Current view of the global state machine
    previous_state = State.NONE  # State "undo" support
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
        lines_printed = 0

        if cls.state == cls.State.HELP:
            # Print the header
            put("=== HELP ===\n")
            put("\n")
            lines_printed += 2
            # Print help text
            for line in cls.HELP_TEXT:
                put(line + "\n")
            lines_printed += len(cls.HELP_TEXT)

        elif cls.state == cls.State.LIST_VIEW:
            # Print the header
            put("=== LISTS ===\n")
            put("\n")
            lines_printed += 2
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
            lines_printed += len(cls.lists)

        # Print newlines until we're 2 lines away from the bottom
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
        user_input = UserInput.parse(cmd)

        if cls.state == cls.State.HELP:
            # Any input exits help state
            cls._undo_state()

        elif user_input.keyword == "exit":
            # Terminate main loop
            cls._change_state(cls.State.SHUTDOWN)
            put("Goodbye!\n")

        elif user_input.keyword == "help":
            # Switch to help state
            cls._change_state(cls.State.HELP)
            cls.last_result = "Help displayed. Input anything to return."

        elif cmd == "":
            # Empty command. User is confused?
            cls.last_result = "Type \"help\" for assistance."

        else:
            cls.last_result = Fore.RED + "Unknown command." + Style.RESET_ALL

    @classmethod
    def _change_state(cls, new_state):
        """Switch state to a new one

        :param new_state: The new state to replace the current one
        :type new_state: :class:`TUI.State`
        """
        cls.previous_state = cls.state
        cls.state = new_state

    @classmethod
    def _undo_state(cls):
        """Undo the most recent state change
        """
        cls.state = cls.previous_state
        cls.previous_state = cls.State.NONE
        cls.last_result = "Welcome to Lists."


TUI.run()
