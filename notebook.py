import json
from collections.abc import Sequence


class Notebook(Sequence):
    """Container class for all lists owned by the user
    """

    def __init__(self):
        """Constructor method
        """
        self._lists = []

    @classmethod
    def from_json(cls, json_data):
        """Create a new notebook instance from JSON representation

        :param json_data: JSON string, as previously generated with serialize()
        :type json_data: str
        """
        print(json_data)
        return Notebook()


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
            "version": 1,  # For future backwards compatibility
            "lists": [lst.data() for lst in self._lists]
        }

    def serialize(self):
        """Return the notebook contents as a JSON string

        :return: The JSON representation of the notebook
        :rtype: str
        """
        return json.dumps(self.data())
