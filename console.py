from colorama import Cursor


def put(text):
    """Print a string without any appended newline

    :param text: The string to print
    :type text: str
    """
    print(text, end="")


def clear(console_size):
    """Clear the screen, and position the cursor at the top

    :param console_size: Size of the console as (rows, columns)
    :type console_size: tuple
    """
    put("\n" * console_size[1])
    put(Cursor.POS(0, 0))
