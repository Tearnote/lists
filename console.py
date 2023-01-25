def put(text):
    """Print a string without any appended newline

    :param text: The string to print
    :type text: str
    :return: Number of characters printed
    :rtype: int
    """
    print(text, end="")
    return len(text)
