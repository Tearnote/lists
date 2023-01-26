from enum import Enum, auto

from colorama import just_fix_windows_console, Fore, Style

from config import Config
from input import UserInput, Command
from list import List
from notebook import Notebook
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
        SETTINGS = auto()  # Program configuration
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
    active_list = None  # Reference to currently viewed list in task view

    list_view_commands = []  # Set of commands available in LIST_VIEW state
    task_view_commands = []  # Set of commands available in TASK_VIEW state
    settings_commands = []  # Set of commands available in SETTINGS state

    last_result = "Welcome to Lists."  # Feedback from the most recent command
    help_text = []  # List of lines shown on the screen in the help state

    notebook = Notebook()  # All to-do lists owned by the user

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
        cls.settings_commands.append(exit_command)
        back_command = Command("back", cls._cmd_back, [
            f"Syntax: {Fore.GREEN}back{Style.RESET_ALL}",
            "",
            "Return to the previous screen. For example, in task view,",
            "it will bring you back to list view."
        ])
        cls.task_view_commands.append(back_command)
        cls.settings_commands.append(back_command)
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
        cls.settings_commands.append(help_command)
        settings_command = Command("settings", cls._cmd_settings, [
            f"Syntax: {Fore.GREEN}settings{Style.RESET_ALL}",
            "",
            "Enter the settings. Here you can change some program behavior,",
            "as well as storage credentials. All settings are",
            "automatically saved."
        ])
        cls.list_view_commands.append(settings_command)
        list_enter_command = Command("", cls._cmd_list_enter, [],
                                     has_index_arg=True,
                                     index_arg_required=True)
        cls.list_view_commands.append(list_enter_command)
        list_add_command = Command("add", cls._cmd_list_add, [
            f"Syntax: {Fore.GREEN}add ...{Style.RESET_ALL}",
            "",
            "Add a new empty list with the provided name. After adding",
            "the list, you will probably want to enter it with",
            "the \"#\" command (just the list index), and add some tasks to it."
        ], has_text_arg=True, text_arg_required=True)
        cls.list_view_commands.append(list_add_command)
        list_remove_command = Command("remove", cls._cmd_list_remove, [
            f"Syntax: {Fore.GREEN}remove #{Style.RESET_ALL}",
            "",
            "Remove the list under the given index. Be very careful with this",
            "command, and always double-check the index - there is currently",
            "no way to undo this operation."
        ], has_index_arg=True, index_arg_required=True)
        cls.list_view_commands.append(list_remove_command)
        list_rename_command = Command("rename", cls._cmd_list_rename, [
            f"Syntax: {Fore.GREEN}rename #{Style.RESET_ALL}",
            "",
            "Change the name of a list under the given index. The contents",
            "of the list stay unchanged."
        ], has_index_arg=True, index_arg_required=True, has_text_arg=True,
                                      text_arg_required=True)
        cls.list_view_commands.append(list_rename_command)
        task_add_command = Command("add", cls._cmd_task_add, [
            f"Syntax: {Fore.GREEN}add #{Style.RESET_ALL}",
            "",
            "Add a task to the list. The task will be added at the end,",
            "in an un-done state."
        ], has_text_arg=True, text_arg_required=True)
        cls.task_view_commands.append(task_add_command)
        task_remove_command = Command("remove", cls._cmd_task_remove, [
            f"Syntax: {Fore.GREEN}remove #{Style.RESET_ALL}",
            "",
            "Remove the task under the given index. Be very careful with this",
            "command, and always double-check the index - there is currently",
            "no way to undo this operation. Consider marking the task as done",
            "instead."
        ], has_index_arg=True, index_arg_required=True)
        cls.task_view_commands.append(task_remove_command)
        task_rename_command = Command("rename", cls._cmd_task_rename, [
            f"Syntax: {Fore.GREEN}rename #{Style.RESET_ALL}",
            "",
            "Edit the task under the given index. The task will stay marked",
            "as done or priority, only the text will change."
        ], has_index_arg=True, index_arg_required=True, has_text_arg=True,
                                      text_arg_required=True)
        cls.task_view_commands.append(task_rename_command)
        task_done_command = Command("done", cls._cmd_task_done, [
            f"Syntax: {Fore.GREEN}done #{Style.RESET_ALL}",
            "",
            "Mark a task as done, or undo the mark to turn the task active",
            "again. In the settings you can choose whether done tasks are",
            "just greyed out, printed with replacement text,",
            "or skipped entirely."
        ], has_index_arg=True, index_arg_required=True)
        cls.task_view_commands.append(task_done_command)
        task_prio_command = Command("prio", cls._cmd_task_prio, [
            f"Syntax: {Fore.GREEN}prio #{Style.RESET_ALL}",
            "",
            "Mark a task as priority, or undo the mark to restore normal",
            "priority. This change is purely visual - priority tasks are",
            "printed with a color accent. It has no effect on tasks marked",
            "as done."
        ], has_index_arg=True, index_arg_required=True)
        cls.task_view_commands.append(task_prio_command)
        settings_set_command = Command("set", cls._cmd_settings_set, [
            f"Syntax: {Fore.GREEN}set # ...",
            "",
            "Change a setting under the provided index to a different value.",
            "If a list of values is show to the right of the setting,",
            "the value must match one of them."
        ], has_index_arg=True, index_arg_required=True, has_text_arg=True,
                                       text_arg_required=True)
        cls.settings_commands.append(settings_set_command)

        # Set up test content
        Config.set("print_done_tasks", "yes")
        test_list = List("Main")
        test_list.tasks.append(Task("Hello world!"))
        test_list.tasks.append(Task("How are you?"))
        test_list.tasks.append(Task("I'm fine, thanks"))
        test_list.tasks.append(Task("The weather is horrible"))
        test_list.tasks.append(Task("It's freezing and wet"))
        test_list.tasks[0].done = True
        test_list.tasks[2].prio = True
        test_list.tasks[3].done = True
        test_list.tasks[4].done = True
        cls.notebook.add(test_list)

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
            put(f"{cls.notebook}\n")

        if cls.state == cls.State.SETTINGS:
            # Print the header
            put_at(0, 0, "=== SETTINGS ===\n")
            put("\n")
            put(Config.print())

        if cls.state == cls.State.TASK_VIEW:
            # Print the header
            put_at(0, 0, "=== TASKS ===\n")
            put("\n")

            # Print the tasks
            put(cls.active_list)

        if (
                cls.state == cls.State.LIST_VIEW or
                cls.state == cls.State.TASK_VIEW or
                cls.state == cls.State.SETTINGS):
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

        except (IndexError, ValueError) as e:
            cls.last_result = f"{Fore.RED}{e}{Style.RESET_ALL}"

        except StopIteration:  # Command not found in list
            cls.last_result = (
                f"{Fore.RED}"
                f"Unknown command "
                f"\"{user_input.keyword}\""
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
        if cls.state == cls.State.SETTINGS:
            return cls.settings_commands
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
    def _cmd_back(cls, *_):
        """Return to the previous screen
        """
        cls._undo_state()

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
    def _cmd_list_add(cls, *args):
        """Add a new list

        :param *args: Tuple of (_, text)
        """
        cls.notebook.add(List(args[1]))
        cls.last_result = f"List \"{args[1]}\" added."

    @classmethod
    def _cmd_list_remove(cls, *args):
        """Remove a list

        :param *args: Tuple of (index, _)
        """
        removed_list = cls.notebook.remove(args[0])
        cls.last_result = f"List \"{removed_list.name}\" removed."

    @classmethod
    def _cmd_list_rename(cls, *args):
        """Rename a list

        :param *args: Tuple of (index, text)
        """
        renamed_list = cls.notebook[args[0]]
        old_name = renamed_list.name
        renamed_list.name = args[1]
        cls.last_result = f"List \"{old_name}\" renamed to \"{args[1]}\"."

    @classmethod
    def _cmd_list_enter(cls, *args):
        """Enter a list

        :param *args: Tuple of (index, _)
        """
        cls.active_list = cls.notebook[args[0]]
        cls.last_result = f"Viewing list \"{cls.active_list.name}\"."
        cls._change_state(cls.State.TASK_VIEW)

    @classmethod
    def _cmd_task_add(cls, *args):
        """Add a new task to active list

        :param *args: Tuple of (_, text)
        """
        cls.active_list.tasks.append(Task(args[1]))
        cls.last_result = f"Task \"{args[1]}\" added."

    @classmethod
    def _cmd_task_remove(cls, *args):
        """Remove a task from active list

        :param *args: Tuple of (index, _)
        """
        tasks = cls.active_list.tasks
        index = args[0] - 1

        # Bound check
        if index < 0 or index >= len(tasks):
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no task with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
            return

        task_name = tasks[index].body
        tasks.pop(index)
        cls.last_result = f"Task \"{task_name}\" removed."

    @classmethod
    def _cmd_task_rename(cls, *args):
        """Rename a task

        :param *args: Tuple of (index, text)
        """
        tasks = cls.active_list.tasks
        index = args[0] - 1

        # Bound check
        if index < 0 or index >= len(tasks):
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no task with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
            return

        old_name = tasks[index].body
        tasks[index].body = args[1]
        cls.last_result = f"Task \"{old_name}\" renamed to \"{args[1]}\"."

    @classmethod
    def _cmd_task_done(cls, *args):
        """Toggle a task's done status

        :param *args: Tuple of (index, _)
        """
        tasks = cls.active_list.tasks
        index = args[0] - 1

        # Bound check
        if index < 0 or index >= len(tasks):
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no task with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
            return

        neg = "not " if tasks[index].done else ""
        tasks[index].done = not tasks[index].done
        cls.last_result = f"Task \"{tasks[index].body}\" marked as {neg}done."

    @classmethod
    def _cmd_task_prio(cls, *args):
        """Toggle a task's prio status

        :param *args: Tuple of (index, _)
        """
        tasks = cls.active_list.tasks
        index = args[0] - 1

        # Bound check
        if index < 0 or index >= len(tasks):
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no task with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
            return

        neg = "not " if tasks[index].prio else ""
        tasks[index].prio = not tasks[index].prio
        cls.last_result = f"Task \"{tasks[index].body}\" marked as {neg}priority."

    @classmethod
    def _cmd_settings(cls, *_):
        """Switch to settings state
        """

        cls.last_result = "Settings displayed."
        cls._change_state(cls.State.SETTINGS)

    @classmethod
    def _cmd_settings_set(cls, *args):
        """Change a setting value

        :param *args: Tuple of (index, value)
        """
        try:
            Config.set_at(args[0], args[1])
        except IndexError:
            cls.last_result = (
                f"{Fore.RED}"
                f"There is no setting with index "
                f"\"{args[0]}\"."
                f"{Style.RESET_ALL}"
            )
        except ValueError:
            cls.last_result = (
                f"{Fore.RED}"
                f"\"{args[1]}\""
                f" is not an allowed value for setting "
                f"\"{Config.description_at(args[0])}\"."
                f"{Style.RESET_ALL}"
            )
        else:
            cls.last_result = (
                f"Setting "
                f"\"{Config.description_at(args[0])}\""
                f" changed to "
                f"\"{args[1]}\".")
