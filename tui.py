from enum import Enum, auto

from colorama import just_fix_windows_console, Fore, Style, Cursor

from config import Config
from input import UserInput, Command
from list import List
from task import Task
from console import put, clear, put_at


class TUI:
    """Runs the interactive terminal-based interface for the app
    """

    class State(Enum):
        """Symbols representing possible states of the UI
        """
        NONE = 0  # Initial state
        HELP = auto()  # Help screen
        LIST_VIEW = auto()  # Displaying list overview
        TASK_VIEW = auto()  # Displaying entries of a single list
        SHUTDOWN = auto()  # Shutdown requested

    CONSOLE_SIZE = (80, 24)  # (w,h) column/row count
    SIDE_PANE_WIDTH = 16
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

    list_view_commands = []  # Set of commands available in LIST_VIEW state
    task_view_commands = []  # Set of commands available in TASK_VIEW state

    last_result = "Welcome to Lists."  # Feedback from the most recent command
    help_text = []  # List of lines shown on the screen in the help state

    lists = []  # All to-do lists owned by the user
    active_list = 0  # Currently viewed list in task view

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
        cls.task_view_commands.append(exit_command)
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
        cls.task_view_commands.append(help_command)
        add_command = Command("add", cls._cmd_add, [
            f"Syntax: {Fore.GREEN}add ...{Style.RESET_ALL}",
            "",
            "Add a new empty list with the provided name. After adding",
            "the list, you will probably want to enter it with",
            "the \"#\" command (just the list index), and add some tasks to it."
        ], has_text_arg=True, text_arg_required=True)
        enter_command = Command("", cls._cmd_enter, [],  # Help cannot be viewed
                                has_index_arg=True,
                                index_arg_required=True)
        cls.list_view_commands.append(enter_command)
        cls.list_view_commands.append(add_command)
        remove_command = Command("remove", cls._cmd_remove, [
            f"Syntax: {Fore.GREEN}remove #{Style.RESET_ALL}",
            "",
            "Remove the list under the given index. Be very careful with this",
            "command, and always double-check the index - there is currently",
            "no way to undo this operation."
        ], has_index_arg=True, index_arg_required=True)
        cls.list_view_commands.append(remove_command)
        rename_command = Command("rename", cls._cmd_rename, [
            f"Syntax: {Fore.GREEN}rename #{Style.RESET_ALL}",
            "",
            "Change the name of a list under the given index. The contents",
            "of the list stay unchanged."
        ], has_index_arg=True, index_arg_required=True, has_text_arg=True,
                                 text_arg_required=True)
        cls.list_view_commands.append(rename_command)

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
            put_at(0, cls.CONSOLE_SIZE[1] - 1, "> ")
            command = input()
            cls._parse(command)

    @classmethod
    def _render(cls):
        """Redraw the screen contents
        """
        clear(cls.CONSOLE_SIZE)

        if cls.state == cls.State.HELP:
            # Print the header
            put_at(0, 0, "=== HELP ===\n")
            put("\n")
            # Print help text
            for line in cls.help_text:
                put(f"{line}\n")

        if cls.state == cls.State.LIST_VIEW:
            # Print the header
            put_at(0, 0, "=== LISTS ===\n")
            put("\n")

            # Print the lists
            for i in range(len(cls.lists)):
                lst = cls.lists[i]
                idx = f"#{i + 1}"
                name = lst.name
                done_count = lst.count_done()
                task_count = len(lst.tasks)
                badge = ""
                if task_count == 0:
                    badge = "empty"
                else:
                    badge = f"{done_count}/{task_count}"
                    if done_count == task_count:
                        badge += ", done!"
                put(f"{idx} {name} ({badge})\n")

        if cls.state == cls.State.TASK_VIEW:
            # Print the header
            put_at(0, 0, "=== TASKS ===\n")
            put("\n")

            # Print the tasks
            put(cls.lists[cls.active_list])

        if cls.state == cls.State.LIST_VIEW or cls.state == cls.State.TASK_VIEW:
            # Print the sidebar
            sidebar_offset = cls.CONSOLE_SIZE[0] - cls.SIDE_PANE_WIDTH - 1
            y_pos = 0
            put_at(sidebar_offset, y_pos, f" === COMMANDS ===\n")
            y_pos += 1
            for command in cls._get_command_list():
                for invocation in command.invocations():
                    put_at(sidebar_offset, y_pos, f"| {invocation}\n")
                    y_pos += 1

        # Print the result message
        put_at(0, cls.CONSOLE_SIZE[1] - 2, f"{cls.last_result}\n")

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
    def _get_command_list(cls):
        """Return the current state's command list

        :return: list of currently applicable :class:`Command`s
        :rtype: list
        """
        if cls.state == cls.State.LIST_VIEW:
            return cls.list_view_commands
        if cls.state == cls.State.TASK_VIEW:
            return cls.task_view_commands
        raise AssertionError  # This should be unreachable

    @classmethod
    def _find_command(cls, keyword):
        """Return a command from the currently available state

        :param keyword: Name of the commend
        :type keyword: str
        :return: Found command object
        :rtype: :class:`Command`
        :raises StopIteration: Command couldn't be found
        """
        command_list = cls._get_command_list()
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

    @classmethod
    def _cmd_add(cls, *args):
        """Add a new list

        :param *args: Tuple of (_, text)
        """
        cls.lists.append(List(args[1]))
        cls.last_result = f"List \"{args[1]}\" added."

    @classmethod
    def _cmd_remove(cls, *args):
        """Remove a list

        :param *args: Tuple of (index, _)
        """
        index = args[0] - 1

        # Bound check
        if index < 0 or index >= len(cls.lists):
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no list with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
            return

        list_name = cls.lists[index].name
        cls.lists.pop(index)
        cls.last_result = f"List \"{list_name}\" removed."

    @classmethod
    def _cmd_rename(cls, *args):
        """Rename a list

        :param *args: Tuple of (index, text)
        """
        index = args[0] - 1

        # Bound check
        if index < 0 or index >= len(cls.lists):
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no list with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
            return

        old_name = cls.lists[index].name
        cls.lists[index].name = args[1]
        cls.last_result = f"List \"{old_name}\" renamed to \"{args[1]}\"."

    @classmethod
    def _cmd_enter(cls, *args):
        """Enter a list

        :param *args: Tuple of (index, _)
        """
        index = args[0] - 1

        # Bound check
        if index < 0 or index >= len(cls.lists):
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no list with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
            return

        cls.active_list = index
        cls.last_result = f"Viewing list \"{cls.lists[index].name}\"."
        cls._change_state(cls.State.TASK_VIEW)
