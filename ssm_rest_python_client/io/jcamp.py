from .scidata import get_scidata_base


# Compression encoding for JCAMP
# Reference found on following site under "Compression Table"
#   - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

# Represents the value with a preceding space (compresses whitespace)
SQZ_digits = {
    '@': '+0',
    'A': '+1',
    'B': '+2',
    'C': '+3',
    'D': '+4',
    'E': '+5',
    'F': '+6',
    'G': '+7',
    'H': '+8',
    'I': '+9',
    'a': '-1',
    'b': '-2',
    'c': '-3',
    'd': '-4',
    'e': '-5',
    'f': '-6',
    'g': '-7',
    'h': '-8',
    'i': '-9',
    '+': '+',  # For PAC
    '-': '-',  # For PAC
    ',': ' ',  # For CSV
}

# Difference agaisnt previous character
DIF_digits = {
    '%': 0,
    'J': 1,
    'K': 2,
    'L': 3,
    'M': 4,
    'N': 5,
    'O': 6,
    'P': 7,
    'Q': 8,
    'R': 9,
    'j': -1,
    'k': -2,
    'l': -3,
    'm': -4,
    'n': -5,
    'o': -6,
    'p': -7,
    'q': -8,
    'r': -9,
}

# Duplicates the previous character by value
DUP_digits = {
    'S': 1,
    'T': 2,
    'U': 3,
    'V': 4,
    'W': 5,
    'X': 6,
    'Y': 7,
    'Z': 8,
    's': 9,
}


class UnknownCharacterException(Exception):
    """Exception for unknown character in line of JCAMP-DX file"""


def _parse_duplicate_characters(line):
    """
    Parse duplicate character compression for a line (i.e. DUP characters).
    Valid DUP characters are: [S, T, U, V, W, X, Y, Z]

    Example: Repeat 9 character 3 times with 'U'
        "9U" == "999"

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line in JCAMP-DX file with duplicate characters (DUP)
    Return:
        new_line (str): Processed line with duplicates added in
    """
    new_line = ""
    for i, char in enumerate(line):
        if (char in DUP_digits):
            # Get number of duplicates to multiply by
            # NOTE: subtract one since we will already have one character from
            #       the original one we are duplicating from.
            nduplicates = DUP_digits[char] - 1
            new_line += line[i-1] * nduplicates
        else:
            new_line += char
    return "".join(new_line)


def _parse_line(line):
    """
    Parse a non-header line of the JCAMP-DX file format

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line in JCAMP-DX file to parse
    Return:
        values (list[float]): List for the values found on the line
    """
    line = ' '.join(line.split())

    # process the duplicate characters (DUP_digits)
    DUP_set = set(DUP_digits)
    if any(char in DUP_set for char in line):
        line = _parse_duplicate_characters(line)

    DIF = False
    num = ''
    values = []
    for char in line:
        if char.isdigit() or char == '.':
            num += char

        elif char == ' ':
            if num:
                value = float(num)
                values.append(value)
            num = ''
            DIF = False

        elif char in SQZ_digits:
            if num:
                value = float(num)
                values.append(value)
            num = SQZ_digits[char]
            DIF = False

        elif char in DIF_digits:
            if num:
                value = float(num)
                if DIF:
                    value = float(num) + values[-1]
                values.append(value)
            num = str(DIF_digits[char])
            DIF = True
        else:
            msg = f"Unknown character {char} encountered"
            raise UnknownCharacterException(msg)
    if num:
        value = float(num)
        if DIF:
            value = float(num) + values[-1]
        values.append(value)

    return values


def read_jcamp(filename):
    """
    Reader for JCAMP-DX files to SciData JSON-LD dictionary
    JCAMP-DX is Joint Committee on Atomic and Molecular Physical Data eXchange
        JCAMP-DX URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename to read from for JCAMP-DX files
    Return:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    scidata_dict = get_scidata_base()
    return scidata_dict


def write_jcamp(filename, scidata_dict):
    """
    Writer for SciData JSON-LD dictionary to JCAMP-DX files.
    JCAMP-DX is Joint Committee on Atomic and Molecular Physical Data eXchange
        JCAMP-DX URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename for JCAMP-DX file
        scidata_dict (dict): SciData JSON-LD dictionary to write out
    """
    pass
