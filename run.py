from enum import Enum, auto
from functools import reduce

from colorama import just_fix_windows_console, Fore, Style
from util import put


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
    :type callback: function(index: int, text: str)
    :param help_text: Text shown about this command on the help screen
    :type help_text: list of str
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

    class MissingArgument(ValueError):
        """User didn't provide the required arguments
        """
        pass

    class TooManyArguments(ValueError):
        """User provided an extraneous argument
        """
        pass

    class InvalidIndex(ValueError):
        """User-provided index cannot be converted to int
        """
        pass

    def __init__(self, keyword, callback, help_text,
                 has_index_arg=False, index_arg_required=False,
                 has_text_arg=False, text_arg_required=False):
        """Constructor method
        """
        self.keyword = keyword
        self.callback = callback
        self.help_text = help_text
        self.has_index_arg = has_index_arg
        self.index_arg_required = index_arg_required
        self.has_text_arg = has_text_arg
        self.text_arg_required = text_arg_required

    def validate_and_run(self, user_input):
        """Confirm that user's input has correct arguments, and run the callback

        :param user_input: Parsed user input string
        :type user_input: :class:`UserInput`
        :raises ValueError: Invalid command for the input
        :raises Command.MissingArgument: User didn't provide enough arguments
        :raises Command.TooManyArguments: User provided too many arguments
        :raises Command.InvalidIndex: User provided a non-integer index
        """
        if self.keyword != user_input.keyword:
            raise ValueError  # This should not happen to begin with

        # Extract params
        if self.has_index_arg and not self.has_text_arg:
            index = user_input.args
            text = ""
        elif not self.has_index_arg and self.has_text_arg:
            index = ""
            text = user_input.args
        else:
            index = user_input.index_arg
            text = user_input.text_arg

        # Validate params
        if self.index_arg_required and index == "":
            raise self.MissingArgument
        if self.text_arg_required and text == "":
            raise self.MissingArgument
        if not self.has_index_arg and index != "":
            raise self.TooManyArguments
        if not self.has_text_arg and text != "":
            raise self.TooManyArguments

        # Convert index to integer
        index_int = -1
        if index != "":
            try:
                index_int = int(index)
            except ValueError:
                raise self.InvalidIndex

        self.callback(index_int, text)


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
    GENERAL_HELP = [
        "Lists is controlled with text commands. You can see the list of",
        "available commands in the pane on the right.",
        "",
        "Commands begin with a keyword, sometimes followed by arguments.",
        "",
        "The argument \"#\" refers to an item index, for example the number",
        "of a list or a task. You can see the index next to each item",
        "on the main screen, for example:",
        "",
        f"#{Fore.GREEN}2{Style.RESET_ALL} Wash the dishes",
        "",
        "The argument \"...\" stands for any text of your choice, like",
        "the full description of a new task. Surrounding the text in quotes",
        "is not required.",
        "",
        "You can also receive help on a specific command, like this:",
        "",
        f"help {Fore.GREEN}delete{Style.RESET_ALL}",
    ]

    state = State.NONE  # Current view of the global state machine
    previous_state = State.NONE  # State "undo" support
    last_result = "Welcome to Lists."  # Feedback from the most recent command
    help_text = []  # List of lines shown on the screen in the help state
    lists = []  # All to-do lists owned by the user
    list_view_commands = []  # Set of commands available in LIST_VIEW state

    @classmethod
    def run(cls):
        """Initialize the terminal interface and run the main loop
        """
        # Initialize
        just_fix_windows_console()
        cls.state = cls.State.LIST_VIEW

        # Set up commands
        exit_command = Command("exit", cls._cmd_exit, [
            f"Syntax: {Fore.GREEN}exit{Style.RESET_ALL}",
            "",
            "Leave the program immediately. All changes are saved."
        ])
        cls.list_view_commands.append(exit_command)
        help_command = Command("help", cls._cmd_help, [
            f"Syntax (1): {Fore.GREEN}help{Style.RESET_ALL}",
            f"Syntax (2): {Fore.GREEN}help ...{Style.RESET_ALL}",
            "",
            "In the (1) form, display general help about using Lists.",
            "",
            "In the (2) form, display help about a specific command.",
            "The text argument is the name of the command, without any symbols",
            "or arguments. The command must exist in the current view, so, for",
            "example, in task view you won't be able to get help about",
            "list-specific commands."
        ], has_text_arg=True)
        cls.list_view_commands.append(help_command)

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
            for line in cls.help_text:
                put(line + "\n")
            lines_printed += len(cls.help_text)

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
        # Special cases
        if cls.state == cls.State.HELP:
            # Any input exits help state
            cls._undo_state()
            return
        if cmd == "":
            # Empty command. User is confused?
            cls.last_result = "Type \"help\" for assistance."
            return

        # Command parsing and execution
        user_input = UserInput.parse(cmd)
        try:
            command = cls._find_command(user_input.keyword)
            command.validate_and_run(user_input)

        except StopIteration:  # Command not found in list
            cls.last_result = (
                f"{Fore.RED}"
                f"Unknown command "
                f"\"{user_input.keyword}\""
                f"{Style.RESET_ALL}")

        except Command.MissingArgument:
            cls.last_result = (
                f"{Fore.RED}"
                f"Not enough arguments provided for command "
                f"\"{user_input.keyword}\""
                f"{Style.RESET_ALL}")

        except Command.TooManyArguments:
            cls.last_result = (
                f"{Fore.RED}"
                f"Too many arguments provided for command "
                f"\"{user_input.keyword}\""
                f"{Style.RESET_ALL}")

        except Command.InvalidIndex:
            cls.last_result = (
                f"{Fore.RED}"
                f"Index value "
                f"\"{user_input.index_arg}\" "
                f"is not valid"
                f"{Style.RESET_ALL}")

    @classmethod
    def _find_command(cls, keyword):
        """Return a command from the currently available state

        :param keyword: Name of the commend
        :type keyword: str
        :return: Found command object
        :rtype: :class:`Command`
        :raises StopIteration: Command couldn't be found
        """
        command_list = []
        if cls.state == cls.State.LIST_VIEW:
            command_list = cls.list_view_commands
        return next(filter(lambda c: c.keyword == keyword, command_list))

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

    @classmethod
    def _cmd_exit(cls, *_):
        """Terminate the main loop
        """
        cls._change_state(cls.State.SHUTDOWN)
        put("Goodbye!\n")

    @classmethod
    def _cmd_help(cls, *args):
        """Switch to help state

        :param *args: Tuple of (_, text)
        """
        _, text = args
        if text != "":  # Command-specific help
            try:
                command = cls._find_command(text)
                cls.help_text = command.help_text
                cls.last_result = (
                    f"Help for command "
                    f"\"{text}\""
                    f" displayed. Input anything to return.")
                cls._change_state(cls.State.HELP)
            except StopIteration:
                cls.last_result = (
                    f"{Fore.RED}"
                    f"Help for command "
                    f"\"{text}\""
                    f" not found"
                    f"{Style.RESET_ALL}"
                )

        else:  # General help
            cls.help_text = cls.GENERAL_HELP
            cls.last_result = "Help displayed. Input anything to return."
            cls._change_state(cls.State.HELP)


TUI.run()
