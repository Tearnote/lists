class Notebook:
    """Container class for all lists owned by the user
    """

    def __init__(self):
        """Constructor method
        """
        self._lists = []

    def get(self, index):
        """Retrieve a list at the provided index

        :param index: one-based index of the list
        :type index: int
        :raises IndexError: Index is out of bounds
        :return: list reference
        :rtype: :class:`List`
        """
        return self._lists[index - 1]

    def add(self, new_list):
        """Add a new list to the end of the notebook

        :param new_list: The list instance to add
        :type new_list: :class:`List`
        """
        self._lists.append(new_list)

    def remove(self, index):
        """Remove the list under given index from the notebook

        :param index: one-based index of the list
        :type index: int
        :raises IndexError: Index is out of bounds
        :return: The removed list
        :rtype: :class:`List`
        """
        return self._lists.pop(index - 1)

    def __str__(self):
        """Return printable form of the notebook as numbered list of lists
        """
        result = ""
        for i in range(len(self._lists)):
            lst = self._lists[i]
            idx = f"#{i + 1}"
            name = lst.name
            done_count = lst.count_done()
            task_count = len(lst.tasks)
            if task_count == 0:
                badge = "empty"
            else:
                badge = f"{done_count}/{task_count}"
                if done_count == task_count:
                    badge += ", done!"
            if i != 0:
                result += "\n"
            result += f"{idx} {name} ({badge})"
        return result
