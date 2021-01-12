import numpy as np
import re

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


class UnsupportedDataTypeConfigException(Exception):
    """Exception for an unsupported data type configuration for parsing"""


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


def _reader(filehandle):
    jcamp_dict = {}
    xstart = []
    xnum = []
    y = []
    x = []
    datastart = False
    is_compound = False
    in_compound_block = False
    compound_block_contents = []
    re_num = re.compile(r'\d+')
    lhs = None
    for line in filehandle:
        if not line.strip():
            continue
        if line.startswith('$$'):
            continue

        # Detect the start of a compound block
        if is_compound and line.upper().startswith('##TITLE'):
            in_compound_block = True
            compound_block_contents = [line]
            continue

        # If we are reading a compound block, collect lines into an array to be
        # processed by a recursive call this this function.
        if in_compound_block:
            # Store this line.
            compound_block_contents.append(line)

            # Detect the end of the compound block.
            if line.upper().startswith('##END'):
                # Process the entire block and put it into the children array.
                jcamp_dict['children'].append(_reader(compound_block_contents))
                in_compound_block = False
                compound_block_contents = []
            continue

        # Lines beginning with '##' are header lines.
        if line.startswith('##'):
            line = line.strip('##')
            (lhs, rhs) = line.split('=', 1)
            lhs = lhs.strip().lower()
            rhs = rhs.strip()

            # Convert 'datatype' key -> 'data type'
            if lhs == 'datatype':
                lhs = 'data type'

            # Detect compound files.
            # See table XI in http://www.jcamp-dx.org/protocols/dxir01.pdf
            if (lhs == 'data type') and (rhs.lower() == 'link'):
                is_compound = True
                jcamp_dict['children'] = []

            if rhs.isdigit():
                jcamp_dict[lhs] = int(rhs)
            elif _is_float(rhs):
                jcamp_dict[lhs] = float(rhs)
            else:
                jcamp_dict[lhs] = rhs

            if (lhs in ('xydata', 'xypoints', 'peak table')):
                # This is a new data entry, reset x and y.
                x = []
                y = []
                datastart = True
                datatype = rhs
                continue        # data starts on next line
            elif (lhs == 'end'):
                bounds = [int(i) for i in re_num.findall(rhs)]
                datastart = True
                datatype = bounds
                continue
            elif datastart:
                datastart = False
        elif lhs is not None and not datastart:  # multiline entry
            jcamp_dict[lhs] += '\n{}'.format(line.strip())

        has_points = 'xypoints' in jcamp_dict
        has_data = 'xydata' in jcamp_dict
        has_peak = 'peak table' in jcamp_dict

        if datastart:
            has_points_or_data_or_peak = has_points or has_data or has_peak

            if datatype == '(X++(Y..Y))':
                datavals = _parse_line(line)
                xstart.append(float(datavals[0]))
                xnum.append(len(datavals) - 1)
                for dataval in datavals[1:]:
                    y.append(float(dataval))

            elif has_points_or_data_or_peak and datatype == '(XY..XY)':
                datavals = [v.strip() for v in re.split(r"[,;\s]", line) if v]

                if not all(_is_float(datavals)):
                    continue
                datavals = np.array(datavals)

                x.extend(datavals[0::2])
                y.extend(datavals[1::2])

            else:
                msg = f"Unable to parse setup for {datatype}"
                raise UnsupportedDataTypeConfigException(msg)

    if has_data and jcamp_dict['xydata'] == '(X++(Y..Y))':
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

    return(jcamp_dict)


def _is_float(s):
    '''
    Test if a string, or list of strings, contains a numeric value(s).

    Args:
        s (str or list[str]): The string or list of strings to test.
    Return:
        is_float_bool (bool or list[bool]): A single boolean or list of boolean
             values indicating whether each input can be converted into float.
    '''
    if isinstance(s, tuple) or isinstance(s, list):
        if not all(isinstance(i, str) for i in s):
            raise TypeError("Input {} is not a list of strings".format(s))

        if not s:
            raise ValueError('Input {} is empty'.format(s))

        bool_list = list(True for i in range(0, len(s)))
        for i in range(0, len(s)):
            try:
                float(s[i])
            except ValueError:
                bool_list[i] = False
        return(bool_list)

    else:
        if not isinstance(s, str):
            raise TypeError("Input '%s' is not a string" % (s))

        try:
            float(s)
            return True
        except ValueError:
            return False


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
    # Extract jcamp file data
    with open(filename, 'r') as fileobj:
        data = _reader(fileobj)
    data['filename'] = filename

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
