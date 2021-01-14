import numpy as np
import re

from .scidata import get_scidata_base

_DATA_FORMAT_XYXY = '(XY..XY)'
_DATA_FORMAT_XYYY = '(X++(Y..Y))'
_DATA_FORMATS = (_DATA_FORMAT_XYXY, _DATA_FORMAT_XYYY)
_DATA_TYPE_KEY = "data type"
_DATA_XY_TYPE_KEY = "xy data type"
_DATA_XY_TYPES = ('xydata', 'xypoints', 'peak table')
_DATA_LINK = "link"
_CHILDREN = "children"


class UnknownCharacterException(Exception):
    """Exception for unknown character in line of JCAMP-DX file"""


class UnsupportedDataTypeConfigException(Exception):
    """Exception for an unsupported data type configuration for parsing"""


class MultiHeaderKeyException(Exception):
    """Exception for finding multiple header keys in a single line"""


# Compression encoding dictionaries for JCAMP
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


def _is_float(strings):
    '''
    Test if a string, or list of strings, contains a numeric value(s).

    Args:
        strings (str or list[str]): The string or list of strings to test.

    Returns:
        is_float_bool (bool or list[bool]): A single boolean or list of boolean
             values indicating whether each input can be converted into float.

    Raises:
        TypeError: If passing a list and elements are not strings or single
            element is not a string
        ValueError: If passing empty list
    '''
    if isinstance(strings, tuple) or isinstance(strings, list):
        if not all(isinstance(i, str) for i in strings):
            raise TypeError("Input {} not a list of strings".format(strings))

        if not strings:
            raise ValueError('Input {} empty'.format(strings))

        bool_list = list(True for i in range(0, len(strings)))
        for i in range(0, len(strings)):
            try:
                float(strings[i])
            except ValueError:
                bool_list[i] = False
        return bool_list

    else:
        if not isinstance(strings, str):
            raise TypeError("Input '%s' is not a string" % (strings))

        try:
            float(strings)
            return True
        except ValueError:
            return False


def _parse_dataset_duplicate_characters(line):
    """
    Parse duplicate character compression for a line (i.e. DUP characters).
    Valid DUP characters are: [S, T, U, V, W, X, Y, Z]

    Example: Repeat 9 character 3 times with 'U'
        "9U" == "999"

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line in JCAMP-DX file with duplicate characters (DUP)

    Returns:
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


def _parse_dataset_line_single_x_multi_y(line):
    """
    Parse a JCAMP data line when using the format '(X++(Y..Y))',
    where we have one X column and multiple Y columns on one line.
    Handles decoding JCAMP compression encoding.

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line from JCAMP for data of '(X++(Y..Y))' format

    Returns:
        values (list[float]): List of float values for the line

    Raises:
        UnkownCharacterException: If we find a character that is neither
            a valid compression character or number.
    """
    # process the duplicate characters (DUP_digits)
    DUP_set = set(DUP_digits)
    if any(char in DUP_set for char in line):
        line = _parse_dataset_duplicate_characters(line)

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
            msg = f"Unknown character {char} encountered in line {line}"
            raise UnknownCharacterException(msg)

    if num:
        value = float(num)
        if DIF:
            value = float(num) + values[-1]
        values.append(value)
    return values


def _parse_dataset_line(line, data_format):
    """
    Parse a data line of the JCAMP-DX file format for the given data format.
    Handles decoding JCAMP compression encoding.

    Reference found on following site under "Compression Table"
        - http://wwwchem.uwimona.edu.jm/software/jcampdx.html

    Args:
        line (str): Line in JCAMP-DX file to parse
        data_format (str): Format of data. Choices: ['(XY..XY)', '(X++(Y..Y))']

    Returns:
        values (list[float]): List of float values for the line
    """
    if data_format not in _DATA_FORMATS:
        msg = f'Data format {data_format} not supported type: {_DATA_FORMATS}'
        raise Exception(msg)

    if data_format == _DATA_FORMAT_XYXY:
        values = [v.strip() for v in re.split(r"[,;\s]", line) if v]

    if data_format == _DATA_FORMAT_XYYY:
        line = ' '.join(line.split())
        values = _parse_dataset_line_single_x_multi_y(line)

    return values


def _parse_header_get_dict(line, datastart):
    """
    Parse the header line, returning a dictionary for the key-value found
    and if we are starting into the data section.

    Args:
        line (str): Line to parse as a JCAMP header
        datastart (bool): Current flag for if we are in a data section

    Returns:
       header_dict (dict): Dictionary with header keys found.
                           Will mostly return a single key-value pair but
                           for some will return multiple pairs
                           Example: A compound file will return the extra
                           {'children': []} pair when detected.
        datastart (bool): Updated flag for if we are inside a data section
    """
    header_dict = {}

    if line.startswith('##'):
        # Get key-value from header line
        line = line.strip('##')
        (key, value) = line.split('=', 1)
        key = key.strip().lower()
        value = value.strip()

        # Convert 'datatype' key -> _DATA_TYPE_KEY
        if key == 'datatype' or key == 'data type':
            key = _DATA_TYPE_KEY

        # Detect compound files.
        # See table XI in http://www.jcamp-dx.org/protocols/dxir01.pdf
        if (key == _DATA_TYPE_KEY) and (value.lower() == _DATA_LINK):
            header_dict[_CHILDREN] = []

        # Put key-value into JCAMP header dictionary for output
        if value.isdigit():
            header_dict[key] = int(value)
        elif _is_float(value):
            header_dict[key] = float(value)
        else:
            header_dict[key] = value

        # Figure out if we are starting a new data entry
        if (key in _DATA_XY_TYPES):
            datastart = True
            header_dict[_DATA_XY_TYPE_KEY] = value
        elif (key == 'end'):
            datastart = True
        elif datastart:
            datastart = False

    return header_dict, datastart


def _parse_header_line(line, jcamp_dict, datastart=False, last_key=None):
    """
    Parse the JCAMP header line and update the output JCAMP dictionary.

    Args:
        line (str):
        jcamp_dict (dict):
        datastart (bool, optional):
        last_key (str, optional):

    Returns:
        (jcamp_dict, datastart, last_key) (tuple): Tuple
            of the modified JCAMP dictionary, the updated flag for if we are
            in a data section and the last key entered used for updating a
            multiline comment in the header.

    Raises:
        MultiHeaderKeyException: If multiple header keys parsed (should be one)
    """
    header_dict, datastart = _parse_header_get_dict(line, datastart)

    # Get the header key, stripping 'children' key if it is a compound file
    remove_keys = (_CHILDREN, _DATA_XY_TYPE_KEY)
    keys = [k for k in header_dict.keys() if k not in remove_keys]
    if len(keys) > 1:
        msg = f'Found multiple header keys: {keys}'
        raise MultiHeaderKeyException(msg)

    # Check if this is a multiline entry in the header
    is_multiline = last_key and not line.startswith('##') and not datastart
    if is_multiline:
        jcamp_dict[last_key] += '\n{}'.format(line.strip())

    # Just do normal update of jcamp w/ header if not multiline
    elif header_dict:
        jcamp_dict.update(header_dict)
        last_key = keys[0]

    return jcamp_dict, datastart, last_key


def _reader(filehandle):
    jcamp_dict = {}
    xstart = []
    xnum = []
    y = []
    x = []
    datastart = False
    in_compound_block = False
    compound_block_contents = []
    last_key = None
    for line in filehandle:
        # Skip blank or comment lines
        if not line.strip():
            continue
        if line.startswith('$$'):
            continue

        # ===================================
        # Detect the start of a compound block
        is_compound = _CHILDREN in jcamp_dict
        if is_compound and line.upper().startswith('##TITLE'):
            in_compound_block = True
            compound_block_contents = [line]
            continue

        # If we are reading a compound block, collect lines into an array to be
        # processed by a recursive call this this function.
        if in_compound_block:
            compound_block_contents.append(line)

            # Detect the end of the compound block.
            if line.upper().startswith('##END'):
                # Process the entire block and put it into the children array.
                jcamp_dict[_CHILDREN].append(_reader(compound_block_contents))
                in_compound_block = False
                compound_block_contents = []
            continue

        # ===================================
        # Parse header line
        jcamp_dict, datastart, last_key = _parse_header_line(
            line,
            jcamp_dict,
            datastart=datastart,
            last_key=last_key)

        if datastart and not line.startswith('##'):
            if jcamp_dict.get(_DATA_XY_TYPE_KEY) == _DATA_FORMAT_XYYY:
                datavals = _parse_dataset_line(line, _DATA_FORMAT_XYYY)
                xstart.append(float(datavals[0]))
                xnum.append(len(datavals) - 1)
                y.extend([float(f) for f in datavals[1:]])

            elif jcamp_dict.get(_DATA_XY_TYPE_KEY) == _DATA_FORMAT_XYXY:
                datavals = _parse_dataset_line(line, _DATA_FORMAT_XYXY)
                x.extend(datavals[0::2])
                y.extend(datavals[1::2])

            else:
                msg = f"Unable to parse data: {jcamp_dict[_DATA_XY_TYPE_KEY]}"
                raise UnsupportedDataTypeConfigException(msg)

    # ===================================
    if jcamp_dict.get(_DATA_XY_TYPE_KEY) == _DATA_FORMAT_XYYY:
        xstart.append(jcamp_dict['lastx'])
        x = np.array([])
        for n in range(len(xnum)-1):
            dx = (xstart[n+1] - xstart[n]) / xnum[n]
            x = np.append(x, xstart[n]+(dx*np.arange(xnum[n])))

        if (xnum[len(xnum)-1] > 1):
            numerator = (jcamp_dict['lastx'] - xstart[len(xnum)-1])
            denominator = (xnum[len(xnum)-1] - 1.0)
            dx = numerator / denominator

            xnext = xstart[len(xnum)-1]+(dx*np.arange(xnum[len(xnum)-1]))
            x = np.append(x, xnext)
        else:
            x = np.append(x, jcamp_dict['lastx'])

        y = np.array([float(yval) for yval in y])

    else:
        x = np.array([float(xval) for xval in x])
        y = np.array([float(yval) for yval in y])

    if ('xfactor' in jcamp_dict):
        x = x * jcamp_dict['xfactor']
    if ('yfactor' in jcamp_dict):
        y = y * jcamp_dict['yfactor']

    jcamp_dict['x'] = list(x)
    jcamp_dict['y'] = list(y)

    return jcamp_dict


def _copy_from_dict_to_dict(dict_a, key_a, dict_b, key_b):
    """
    Using dict_a and key_a, add dict_a[key_a] to dict_b[key_b].
    If key_a does not exist in dict_a, just return

    Args:
        dict_a (dict): Dictionary to copy from using key_a
        key_a (str): Key for dict_a to access value to copy to dict_b
        dict_b (dict): Dictionary to copy to at key_b
        key_b (dict): Key for dict_b to store value from dict_a[key_a]
    Returns:
        dict_b (dict): Dictionary w/ new key added (if it exists in dict_a)
    """
    if key_a in dict_a:
        dict_b[key_b] = dict_a[key_a]
    return dict_b


def read_jcamp(filename):
    """
    Reader for JCAMP-DX files to SciData JSON-LD dictionary
    JCAMP-DX is Joint Committee on Atomic and Molecular Physical Data eXchange
        JCAMP-DX URL:  http://jcamp-dx.org/

    Args:
        filename (str): Filename to read from for JCAMP-DX files

    Returns:
        scidata_dict (dict): SciData JSON-LD dictionary
    """
    # Extract jcamp file data
    with open(filename, 'r') as fileobj:
        jcamp_dict = _reader(fileobj)

    # Get a base SciData dict
    scidata_dict = get_scidata_base()

    # Start translating the JCAMP dict -> SciData dict
    graph = scidata_dict['@graph']
    graph = _copy_from_dict_to_dict(jcamp_dict, 'title', graph, 'title')
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
