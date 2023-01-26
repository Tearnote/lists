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
        cmd = cmd.strip()
        keyword, _, args = cmd.partition(" ")
        keyword = keyword.lower()
        args = args.strip()
        index_arg, _, text_arg = args.partition(" ")
        text_arg = text_arg.strip()

        # Special case - index-only command
        if args == "" and keyword.isdecimal():
            args = keyword
            index_arg = keyword
            keyword = ""

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

    def invocations(self):
        """Return all the possible invocations of the command

        :return: A list of strings that represent command invocations
        :rtype: list
        """
        # Special case - index-only
        if self.keyword == "" and self.has_index_arg:
            return ["#"]

        result = []
        if not self.index_arg_required and not self.text_arg_required:
            result.append(f"{self.keyword}")
        if self.has_index_arg and not self.text_arg_required:
            result.append(f"{self.keyword} #")
        if self.has_index_arg and self.has_text_arg:
            result.append(f"{self.keyword} # ...")
        if not self.index_arg_required and self.has_text_arg:
            result.append(f"{self.keyword} ...")
        return result

    def validate_and_run(self, user_input):
        """Confirm that user's input has correct arguments, and run the callback

        :param user_input: Parsed user input string
        :type user_input: :class:`UserInput`
        :raises ValueError: Wrong command or number of arguments
        :raises TypeError: User provided a non-integer index
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
        if (self.index_arg_required and index == "") or (
                self.text_arg_required and text == ""):
            raise ValueError(
                f"Not enough arguments provided for command \"{self.keyword}\""
            )
        if (not self.has_index_arg and index != "") or (
                not self.has_text_arg and text != ""):
            raise ValueError(
                f"Too many arguments provided for command \"{self.keyword}\""
            )

        # Convert index to integer
        index_int = -1
        if index != "":
            try:
                index_int = int(index)
            except ValueError:
                raise TypeError(f"Index value \"{index}\" is not valid")

        self.callback(index_int, text)
