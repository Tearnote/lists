from colorama import Cursor


def put(text):
    """Print a string without any appended newline

    :param text: The string to print
    :type text: str
    """
    print(text, end="")


def put_at(x, y, text):
    """Print a string at a specific console position

    :param x: Horizontal position
    :type x: int
    :param y: Vertical position
    :type y: int
    :param text: The string to print
    :type text: str
    """
    put(f"{Cursor.POS(x + 1, y + 1)}{text}")


def clear(console_size):
    """Clear the screen, and position the cursor at the top

    :param console_size: Size of the console as (rows, columns)
    :type console_size: tuple
    """
    put("\n" * console_size[1])
    put_at(0, 0, "")
