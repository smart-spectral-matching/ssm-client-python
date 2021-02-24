import numpy as np
import pathlib
import pytest

from ssm_rest_python_client.io import jcamp, scidata
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

def test_is_float():
    assert jcamp._is_float('0.09')
    assert jcamp._is_float(['0.09'])
    assert jcamp._is_float(['0.09', '10.0', '10'])
    assert jcamp._is_float(('0.09', '10.0', '10'))

    assert not jcamp._is_float('cat')
    assert jcamp._is_float(['cat']) == [False]
    assert jcamp._is_float(['cat', 'x']) == [False, False]

    mylist = ['cat', 'x', '2', '=', 'cats']
    target = [False, False, True, False, False]
    assert jcamp._is_float(mylist) == target

    with pytest.raises(TypeError):
        jcamp._is_float(0.09)

    with pytest.raises(TypeError):
        jcamp._is_float([0.09])

    with pytest.raises(ValueError):
        jcamp._is_float([])


def test_num_dif_factory():
    # space character
    num, DIF = jcamp._num_dif_factory(' ', '')
    assert num == ''
    assert DIF is False

    # SQZ digits character
    num, DIF = jcamp._num_dif_factory('A', '')
    assert num == '+1'
    assert DIF is False

    # DIF digits character
    num, DIF = jcamp._num_dif_factory('n', '')
    assert num == '-5'
    assert DIF is True


def test_parse_dataset_line():
    target = [99.0, 98.0, 97.0, 96.0, 98.0, 93.0]
    line = "99 98 97 96 98 93"

    assert jcamp._parse_dataset_line(line, jcamp._DATA_FORMAT_XYYY) == target
    assert jcamp._parse_dataset_line(line, jcamp._DATA_FORMAT_XYXY) == target

    data_format = 'BAD FORMAT'
    with pytest.raises(jcamp.UnsupportedDataTypeConfigException):
        jcamp._parse_dataset_line(line, data_format)


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


def test_parse_header_line():
    line = ''
    input_dict = {}
    jcamp_dict, start, last_key = jcamp._parse_header_line(line, input_dict)
    assert jcamp_dict == {}
    assert start is False
    assert last_key is None

    input_dict = {
        'title': "ETHANOL",
        'data type': "INFRARED SPECTRUM",
        'molform': "C2 H6 O"
    }
    jcamp_dict, start, last_key = jcamp._parse_header_line(line, input_dict)
    assert jcamp_dict == input_dict
    assert start is False
    assert last_key is None

    line = "##XUNITS= 1/CM"
    jcamp_dict, start, last_key = jcamp._parse_header_line(line, input_dict)
    input_dict.update({'xunits': '1/CM'})
    assert jcamp_dict == input_dict
    assert start is False
    assert last_key == 'xunits'


def test_extract_description_section():
    description_lines = []
    description_lines.append("CAT: meow")
    description_lines.append("DOG: bark")
    description = jcamp._DESCRIPTION_KEY_SPLIT_CHAR.join(description_lines)
    assert jcamp._extract_description_section(description, "CAT") == "meow"
    assert jcamp._extract_description_section(description, "DOG") == "bark"
    assert jcamp._extract_description_section(description, "EAGLE") == None


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


def test_read_infrared(infrared_ethanol_file):
    scidata_dict = jcamp.read_jcamp(infrared_ethanol_file.absolute())
    defaults = scidata.get_scidata_defaults()

    graph = scidata_dict.get('@graph')
    assert graph['title'] == 'ETHANOL'
    assert graph['publisher'] == 'DOW CHEMICAL COMPANY'
    assert graph['generatedAt'] == 1964

    # Check description has all the keywords from JCAMP file
    description = graph.get("description")
    for jcamp_keyword in ["JCAMP-DX", "COBLENTZ"]:
        assert jcamp_keyword in description

    assert len(graph["author"]) == 1
    assert graph["author"][0]["name"].startswith("COBLENTZ SOCIETY")

    # Methodology
    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    target = defaults["@graph"]["scidata"]["methodology"]
    assert methodology["@id"] == target["@id"]
    assert methodology["@type"] == target["@type"]
    assert len(methodology["evaluation"]) == 1
    assert methodology["evaluation"] == ["experimental"]
    assert len(methodology["aspects"]) == 3
    aspects = methodology["aspects"]
    assert len(aspects[0]["settings"]) == 3
    grating = aspects[0]["settings"][0]["value"]["number"]
    assert grating == "GRATING CHANGED AT 5.0, 7.5, 15.0 MICRON"
    assert aspects[0]["settings"][1]["quantity"] == "length"
    assert aspects[0]["settings"][1]["property"] == "path length"

    # System
    system = scidata_dict["@graph"]["scidata"]["system"]
    target = defaults["@graph"]["scidata"]["system"]
    assert system["@id"] == target["@id"]
    assert system["@type"] == target["@type"]
    assert system["discipline"] == "w3i:Chemistry"
    assert system["subdiscipline"] == "w3i:AnalyticalChemistry"
    assert len(system["facets"]) == 3
    compound_facet = system["facets"][0]
    assert compound_facet["@id"] == "compound/1/"
    assert len(compound_facet["@type"]) == 2
    assert compound_facet["formula"] == "C2 H6 O"
    assert compound_facet["casrn"] == "64-17-5"
    assert compound_facet["name"] == "ETHANOL"
    substance_facet = system["facets"][1]
    assert substance_facet["@id"] == "substance/1/"
    assert len(substance_facet["@type"]) == 1
    assert substance_facet["name"] == "ETHANOL"
    assert substance_facet["phase"] == "GAS"

    # Dataset
    dataset = scidata_dict["@graph"]["scidata"]["dataset"]
    target = defaults["@graph"]["scidata"]["dataset"]
    assert dataset["@id"] == target["@id"]
    assert dataset["@type"] == target["@type"]
    assert len(dataset) == 6
    assert dataset["source"] == "measurement/1"
    assert dataset["scope"] == "material/1"
    assert len(dataset["datagroup"]) == 1
    attributes = dataset["datagroup"][0]["attributes"]
    assert len(attributes) == 11
    assert attributes[0]["property"] == "Number of Data Points"
    assert attributes[0]["value"]["number"] == "3570"
    assert attributes[1]["property"] == "First X-axis Value"
    assert attributes[1]["value"]["number"] == "461.563"
    assert attributes[2]["property"] == "Last X-axis Value"
    assert attributes[2]["value"]["number"] == "3807.5"
    assert attributes[3]["property"] == "Minimum X-axis Value"
    assert attributes[3]["value"]["number"] == "461.563"
    assert attributes[4]["property"] == "Maximum X-axis Value"
    assert attributes[4]["value"]["number"] == "3807.5"
    assert attributes[5]["property"] == "First Y-axis Value"
    assert attributes[5]["value"]["number"] == "0.966"
    assert attributes[6]["property"] == "Last Y-axis Value"
    assert attributes[6]["value"]["number"] == "1.0"
    assert attributes[7]["property"] == "Minimum Y-axis Value"
    assert attributes[7]["value"]["number"] == "0.142"
    assert attributes[8]["property"] == "Maximum Y-axis Value"
    assert attributes[8]["value"]["number"] == "1.024"
    assert attributes[9]["property"] == "X-axis Scaling Factor"
    assert attributes[9]["value"]["number"] == "1.0"
    assert attributes[10]["property"] == "Y-axis Scaling Factor"
    assert attributes[10]["value"]["number"] == "1.0"


def test_read_raman(raman_tannic_acid_file):
    scidata_dict = jcamp.read_jcamp(raman_tannic_acid_file.absolute())
    defaults = scidata.get_scidata_defaults()

    graph = scidata_dict.get('@graph')
    assert graph['title'] == 'tannic acid'
    assert graph['publisher'] == 'Ocean Optics R2000'
    assert graph['generatedAt'] == '2000/10/04 - 14:47'

    # Check description has all the keywords from JCAMP file
    description = graph.get("description")
    for jcamp_keyword in ["JCAMP-DX", jcamp._DATA_FORMAT_XYXY]:
        assert jcamp_keyword in description

    assert len(graph["author"]) == 1
    assert graph["author"][0]["name"].startswith("Augustana College")

    # Methodology
    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    target = defaults["@graph"]["scidata"]["methodology"]
    assert methodology["@id"] == target["@id"]
    assert methodology["@type"] == target["@type"]
    assert len(methodology["evaluation"]) == 1
    assert methodology["evaluation"] == ["experimental"]
    assert len(methodology["aspects"]) == 1

    # System
    system = scidata_dict["@graph"]["scidata"]["system"]
    target = defaults["@graph"]["scidata"]["system"]
    assert system["@id"] == target["@id"]
    assert system["@type"] == target["@type"]
    assert system["discipline"] == "w3i:Chemistry"
    assert system["subdiscipline"] == "w3i:AnalyticalChemistry"

    # Dataset
    dataset = scidata_dict["@graph"]["scidata"]["dataset"]
    target = defaults["@graph"]["scidata"]["dataset"]
    assert dataset["@id"] == target["@id"]
    assert dataset["@type"] == target["@type"]
    assert len(dataset) == 6
    assert dataset["source"] == "measurement/1"
    assert dataset["scope"] == "material/1"
    assert len(dataset["datagroup"]) == 1
    attributes = dataset["datagroup"][0]["attributes"]
    assert len(attributes) == 11
    assert attributes[0]["property"] == "Number of Data Points"
    assert attributes[0]["value"]["number"] == "1949"
    assert attributes[1]["property"] == "First X-axis Value"
    assert attributes[1]["value"]["number"] == "100.595"
    assert attributes[2]["property"] == "Last X-axis Value"
    assert attributes[2]["value"]["number"] == "2854.713"
    assert attributes[3]["property"] == "Minimum X-axis Value"
    assert attributes[3]["value"]["number"] == "100.595"
    assert attributes[4]["property"] == "Maximum X-axis Value"
    assert attributes[4]["value"]["number"] == "2854.713"
    assert attributes[5]["property"] == "First Y-axis Value"
    assert attributes[5]["value"]["number"] == "42.644"
    assert attributes[6]["property"] == "Last Y-axis Value"
    assert attributes[6]["value"]["number"] == "4.667"
    assert attributes[7]["property"] == "Minimum Y-axis Value"
    assert attributes[7]["value"]["number"] == "4.667"
    assert attributes[8]["property"] == "Maximum Y-axis Value"
    assert attributes[8]["value"]["number"] == "300.889"
    assert attributes[9]["property"] == "X-axis Scaling Factor"
    assert attributes[9]["value"]["number"] == "1.0"
    assert attributes[10]["property"] == "Y-axis Scaling Factor"
    assert attributes[10]["value"]["number"] == "1.0"


def test_write_raman(tmp_path, raman_tannic_acid_file):
    scidata_dict = jcamp.read_jcamp(raman_tannic_acid_file.absolute())
    jcamp_dir = tmp_path / "jcamp"
    jcamp_dir.mkdir()
    filename = jcamp_dir / "raman_tannic_acid.jdx"
    jcamp.write_jcamp(filename.absolute(), scidata_dict)
    result = filename.read_text().splitlines()
    target = raman_tannic_acid_file.read_text().splitlines()

    for result_element, target_element in zip(result, target):
        result_list = [x.strip() for x in result_element.split(',')]
        target_list = [x.strip() for x in target_element.split(',')]
        assert result_list == target_list
