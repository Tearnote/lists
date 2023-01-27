from collections.abc import Sequence
from functools import reduce

from colorama import Fore, Style

from config import Config


class List(Sequence):
    """An ordered, printable list of tasks

    :param name: Name of the list
    :type name: str
    """

    def __init__(self, name):
        """Constructor method
        """
        self.name = name
        self._tasks = []

    def __getitem__(self, index):
        """Retrieve a task at the provided index

        :param index: one-based index of the list
        :type index: int
        :raises IndexError: Index is out of bounds
        :return: task reference
        :rtype: :class:`Task`
        """
        pass
        try:
            return self._tasks[index - 1]
        except IndexError:
            raise IndexError(f"There is no task with index {index}")

    def __len__(self):
        """Return the number of tasks

        :return: task count
        :rtype: int
        """
        return len(self._tasks)

    def add(self, new_task):
        """Add a new task to the end of the list

        :param new_task: The task instance to add
        :type new_task: :class:`Task`
        """
        self._tasks.append(new_task)

    def remove(self, index):
        """Remove the task under given index from the list

        :param index: one-based index of the task
        :type index: int
        :raises IndexError: Index is out of bounds
        :return: The removed task
        :rtype: :class:`Task`
        """
        try:
            return self._tasks.pop(index - 1)
        except IndexError:
            raise IndexError(f"There is no task with index {index}")

    def __str__(self):
        """Print the list as numbered tasks, one per line

        Done tasks are greyed out.
        """
        result = ""
        for i in range(len(self._tasks)):
            task = self._tasks[i]
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
        return reduce(lambda acc, t: acc + 1 if t.done else acc, self._tasks, 0)
