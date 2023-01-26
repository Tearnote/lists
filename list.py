from functools import reduce

from colorama import Fore, Style

from config import Config


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
            color = ""
            if task.done:
                color = Fore.LIGHTBLACK_EX
            elif task.prio:
                color = Fore.LIGHTWHITE_EX
            result += f"{color}#{i + 1} {task}{Style.RESET_ALL}\n"

        return result

    def count_done(self):
        """Count how many tasks are done

        :return: The number of tasks in the list that are done
        :rtype: int
        """
        return reduce(lambda acc, t: acc + 1 if t.done else acc, self.tasks, 0)
