from config import Config


class Task:
    """A single entry of a to-do list

    :param body: Body text of the task
    :type body: str
    :param done: `True` if the task is marked as completed, defaults to `False`
    :type done: bool, optional
    :param prio: `True` if the task is marked as priority, defaults to `False`
    :type prio: bool, optional
    """

    def __init__(self, body, done=False, prio=False):
        """Constructor method
        """
        self.body = body
        self.done = done
        self.prio = prio

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

    def data(self):
        """Return a dict representation of the task

        :return: A dictionary holding task details
        :rtype: dict
        """
        return {
            "body": self.body,
            "done": self.done,
            "prio": self.prio
        }
