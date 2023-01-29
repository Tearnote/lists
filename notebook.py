import json
from collections.abc import Sequence

from list import List


class Notebook(Sequence):
    """Container class for all lists owned by the user
    """

    DATA_VERSION = 1
    MAX_LISTS = 19  # Max number of lists before layout overflow

    def __init__(self):
        """Constructor method
        """
        self._lists = []

    def __getitem__(self, index):
        """Retrieve a list at the provided index

        :param index: one-based index of the list
        :type index: int
        :raises IndexError: Index is out of bounds
        :return: list reference
        :rtype: :class:`List`
        """
        try:
            return self._lists[index - 1]
        except IndexError:
            raise IndexError(f"There is no list with index {index}")

    def __len__(self):
        """Return the number of lists

        :return: list count
        :rtype: int
        """
        return len(self._lists)

    def add(self, new_list):
        """Add a new list to the end of the notebook

        :param new_list: The list instance to add
        :type new_list: :class:`List`
        :raises RuntimeError: Too many lists
        """
        if len(self._lists) >= self.MAX_LISTS:
            raise RuntimeError("Reached the maximum allowed number of lists")
        self._lists.append(new_list)

    def remove(self, index):
        """Remove the list under given index from the notebook

        :param index: one-based index of the list
        :type index: int
        :raises IndexError: Index is out of bounds
        :return: The removed list
        :rtype: :class:`List`
        """
        try:
            return self._lists.pop(index - 1)
        except IndexError:
            raise IndexError(f"There is no list with index {index}")

    def __str__(self):
        """Return printable form of the notebook as numbered list of lists
        """
        result = ""
        for i in range(len(self._lists)):
            lst = self._lists[i]
            idx = f"#{i + 1}"
            name = lst.name
            done_count = lst.count_done()
            task_count = len(lst)
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

    def data(self):
        """Return the dict representation of the notebook

        :return: A dictionary holding the notebook contents
        :rtype: dict
        """
        return {
            "version": self.DATA_VERSION,  # For future backwards compatibility
            "lists": [lst.data() for lst in self._lists]
        }

    @classmethod
    def from_data(cls, data):
        """Create a new notebook from dict representation

        :param data: A dictionary as previously returned by data()
        :type data: dict
        :return: A new notebook instance
        :rtype: :class:`Notebook`
        """
        result = Notebook()
        assert data["version"] == cls.DATA_VERSION  # Compatibility check
        result._lists = [List.from_data(lst) for lst in data["lists"]]
        return result

    def serialize(self):
        """Return the notebook contents as a JSON string

        :return: The JSON representation of the notebook
        :rtype: str
        """
        return json.dumps(self.data())

    @classmethod
    def from_json(cls, json_data):
        """Create a new notebook instance from JSON representation

        :param json_data: JSON string, as previously generated with serialize()
        :type json_data: str
        :return: A new notebook instance
        :rtype: :class:`Notebook`
        """
        return Notebook.from_data(json.loads(json_data))
