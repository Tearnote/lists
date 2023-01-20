from colorama import just_fix_windows_console, Fore, Style


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


just_fix_windows_console()

task = Task(Fore.GREEN + "Hello" + Fore.BLUE + " World" + Style.RESET_ALL + "!")
print(task.body)
