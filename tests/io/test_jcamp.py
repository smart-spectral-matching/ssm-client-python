import numpy as np
import pathlib
import pytest

from ssm_rest_python_client.io import jcamp
from tests import TEST_DATA_DIR


@pytest.fixture
def hnmr_ethanol_file():
    """
    Hydrogen NMR JCAMP-DX file for ethanol
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/hnmr_spectra/ethanol_nmr.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "hnmr_ethanol.jdx")
    return p


@pytest.fixture
def infrared_ethanol_file():
    """
    Infrared JCAMP-DX file for ethanol
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/ethanol.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_ethanol.jdx")
    return p


@pytest.fixture
def infrared_ethanol_compressed_file():
    """
    Infrared JCAMP-DX file for ethanol using compression
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/ethanol2.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_ethanol_compressed.jdx")
    return p


@pytest.fixture
def infrared_compound_file():
    """
    Infrared JCAMP-DX compound file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/example_compound_file.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_compound_file.jdx")
    return p


@pytest.fixture
def infrared_multiline_file():
    """
    Infrared JCAMP-DX multiline file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/infrared_spectra/example_multiline_datasets.jdx  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "infrared_multiline_datasets.jdx")
    return p


@pytest.fixture
def mass_ethanol_file():
    """
    Mass spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/mass_spectra/ethanol_ms.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "mass_ethanol.jdx")
    return p


@pytest.fixture
def neutron_emodine_file():
    """
    Inelastic neutron spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/neutron_scattering_spectra/emodine.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "neutron_emodine.jdx")
    return p


@pytest.fixture
def raman_tannic_acid_file():
    """
    Raman spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/raman_spectra/tannic_acid.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "raman_tannic_acid.jdx")
    return p


@pytest.fixture
def uvvis_toluene_file():
    """
    UV-Visible spectroscopy JCAMP-DX file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/nzhagen/jcamp/master/data/uvvis_spectra/toluene.jdx # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "jcamp", "uvvis_toluene.jdx")
    return p


def xy_minmax_checker(testdict):
    tol = 1e-4
    if testdict['x'] and 'minx' in testdict:
        assert isinstance(testdict['x'], list)
        assert isinstance(testdict['y'], list)
        assert len(testdict['x']) == len(testdict['y'])
        assert np.amin(testdict['x']) == pytest.approx(testdict['minx'], tol)
        assert np.amin(testdict['y']) == pytest.approx(testdict['miny'], tol)
        assert np.amax(testdict['x']) == pytest.approx(testdict['maxx'], tol)
        assert np.amax(testdict['y']) == pytest.approx(testdict['maxy'], tol)
    elif 'children' in testdict:
        for child in testdict['children']:
            if ('minx' in testdict):
                assert np.amin(child['x']) == child['minx']
                assert np.amin(child['y']) == child['miny']
                assert np.amax(child['x']) == child['maxx']
                assert np.amax(child['y']) == child['maxy']


# Tests

def test_parse_dataset_duplicate_characters():
    assert jcamp._parse_dataset_duplicate_characters("9U") == "999"


def test_parse_dataset_line_single_x_multi_y():
    target = [99.0, 98.0, 97.0, 96.0, 98.0, 93.0]

    line = "99 98 97 96 98 93"
    assert jcamp._parse_dataset_line_single_x_multi_y(line) == target

    line = "99,98,97,96,98,93"
    assert jcamp._parse_dataset_line_single_x_multi_y(line) == target

    line = "99+98+97+96+98+93"
    assert jcamp._parse_dataset_line_single_x_multi_y(line) == target

    line = "99I8I7I6I8I3"
    assert jcamp._parse_dataset_line_single_x_multi_y(line) == target

    line = "99jjjKn"
    assert jcamp._parse_dataset_line_single_x_multi_y(line) == target

    line = "99jUKn"
    assert jcamp._parse_dataset_line_single_x_multi_y(line) == target

    line = "99 98 *"
    with pytest.raises(jcamp.UnknownCharacterException):
        jcamp._parse_dataset_line_single_x_multi_y(line)


def test_reader_hnmr(hnmr_ethanol_file):
    with open(hnmr_ethanol_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert 'Ethanol' in jcamp_dict.get('title')
    assert jcamp_dict.get('data type') == "LINK"

    children = jcamp_dict.get('children')
    assert len(children) == jcamp_dict.get('blocks')

    atoms = children[0]
    assert 'atomlist' in atoms
    assert atoms.get('block_id') == 1

    assignments = children[1]
    assert assignments.get('block_id') == 2
    assert assignments.get('data type') == "NMR PEAK ASSIGNMENTS"
    assert assignments.get('data class') == "ASSIGNMENTS"

    peaks = children[2]
    assert peaks.get('block_id') == 3
    assert peaks.get('data type') == "NMR SPECTRUM"
    assert peaks.get('data class') == "PEAK TABLE"
    assert peaks.get(jcamp._DATA_XY_TYPE_KEY) == '(XY..XY)'

    xydata = children[3]
    assert xydata.get('block_id') == 4
    assert xydata.get('data type') == "NMR SPECTRUM"
    assert xydata.get('data class') == "XYDATA"
    assert xydata.get(jcamp._DATA_XY_TYPE_KEY) == '(X++(Y..Y))'


def test_reader_infrared(infrared_ethanol_file):
    with open(infrared_ethanol_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == "ETHANOL"
    assert jcamp_dict.get('data type') == "INFRARED SPECTRUM"
    assert jcamp_dict.get('molform') == "C2 H6 O"
    assert jcamp_dict.get(jcamp._DATA_XY_TYPE_KEY) == '(X++(Y..Y))'


def test_reader_infrared_compressed(infrared_ethanol_compressed_file):
    with open(infrared_ethanol_compressed_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == "$$ Begin of the data block"
    assert jcamp_dict.get('data type') == "INFRARED SPECTRUM"
    assert jcamp_dict.get(jcamp._DATA_XY_TYPE_KEY) == '(X++(Y..Y))'


def test_reader_infrared_compound(infrared_compound_file):
    with open(infrared_compound_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == ""
    assert jcamp_dict.get('data type') == "LINK"

    children = jcamp_dict.get('children')
    assert len(children) == jcamp_dict.get('blocks')

    for child in children:
        assert child.get('data type') == "INFRARED SPECTRUM"
        assert child.get(jcamp._DATA_XY_TYPE_KEY) == '(XY..XY)'


def test_reader_infrared_multiline(infrared_multiline_file):
    with open(infrared_multiline_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == "multiline datasets test"
    assert jcamp_dict.get('data type') == "INFRARED SPECTRUM"
    assert jcamp_dict.get(jcamp._DATA_XY_TYPE_KEY) == '(X++(Y..Y))'


def test_reader_mass(mass_ethanol_file):
    with open(mass_ethanol_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == "ethanol"
    assert jcamp_dict.get('data type') == "MASS SPECTRUM"
    assert jcamp_dict.get('data class') == "PEAK TABLE"
    assert jcamp_dict.get(jcamp._DATA_XY_TYPE_KEY) == '(XY..XY)'


def test_reader_neutron(neutron_emodine_file):
    with open(neutron_emodine_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == "Emodine, C15H10O4"
    assert jcamp_dict.get('data type') == "INELASTIC NEUTRON SCATTERING"
    assert jcamp_dict.get(jcamp._DATA_XY_TYPE_KEY) == '(X++(Y..Y))'


def test_reader_raman(raman_tannic_acid_file):
    with open(raman_tannic_acid_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == "tannic acid"
    assert jcamp_dict.get('data type') == "RAMAN SPECTRUM"
    assert jcamp_dict.get(jcamp._DATA_XY_TYPE_KEY) == '(XY..XY)'


def test_reader_uvvis(uvvis_toluene_file):
    with open(uvvis_toluene_file.absolute(), 'r') as fileobj:
        jcamp_dict = jcamp._reader(fileobj)
    xy_minmax_checker(jcamp_dict)

    assert jcamp_dict.get('title') == "Toluene"
    assert jcamp_dict.get('data type') == "UV/VIS SPECTRUM"
    assert jcamp_dict.get('molform') == "C7H8"
    assert jcamp_dict.get(jcamp._DATA_XY_TYPE_KEY) == '(XY..XY)'


def test_read_jcamp(infrared_ethanol_file):
    scidata_dict = jcamp.read_jcamp(infrared_ethanol_file.absolute())
    assert scidata_dict['@graph']['title'] == 'ETHANOL'
