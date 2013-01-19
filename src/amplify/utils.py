import re

def natural_sort(string):
    '''
    This function is meant to be used as a value for the key-argument in
    sorting functions like sorted().

    It makes sure that strings like '2 foo' gets sorted before '11 foo', by
    treating the digits as the value they represent.
    '''

    # Split the string into a list of text and digits, preserving the relative
    # order of the digits.
    components = re.split(r'(\d+)', string)

    # If a part consists of just digits, convert it into an integer. Otherwise
    # we'll just keep the part as it is.
    return [(int(part) if part.isdigit() else part) for part in components]


