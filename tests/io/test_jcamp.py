import numpy as np
import pathlib
import pytest
from typing import List

from ssm_client.io import jcamp
from tests import TEST_DATA_DIR


def _remove_elements_from_list(
    old_list: List[str],
    skip_elements: List[str]
) -> List[str]:
    """
    Utility function for removing elements from a list

    :param old_list: List to remove elements from
    :param skip_elements: List with elements to remove from the list
    :return: New list with the elements removed
    """
    new_list = []
    for element in old_list:
        keep = True
        element_list = [x.strip() for x in element.split(',')]
        for key in skip_elements:
            for x in element_list:
                if key in x:
                    keep = False

        if keep:
            new_list.append(element)

    return new_list


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


# Tests

@pytest.mark.skip("Broken test due to SciDataLib not handling jcamp 'children'")
def test_read_hnmr(hnmr_ethanol_file):
    scidata_dict = jcamp.read_jcamp(hnmr_ethanol_file.resolve())


def test_read_infrared(infrared_ethanol_file):
    scidata_dict = jcamp.read_jcamp(infrared_ethanol_file.resolve())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == 'ETHANOL'
    assert graph['publisher'] == 'DOW CHEMICAL COMPANY'
    description = graph.get("description")
    for jcamp_keyword in ["JCAMP-DX", "COBLENTZ"]:
        assert jcamp_keyword in description

    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    assert len(methodology["aspects"]) == 3
    aspects = methodology["aspects"]
    assert len(aspects[0]["settings"]) == 3
    grating = aspects[0]["settings"][0]["value"]["number"]
    assert grating == "GRATING CHANGED AT 5.0, 7.5, 15.0 MICRON"
    assert aspects[0]["settings"][1]["quantity"] == "length"
    assert aspects[0]["settings"][1]["property"] == "path length"

    system = scidata_dict["@graph"]["scidata"]["system"]
    assert len(system["facets"]) == 3
    compound_facet = system["facets"][0]
    assert compound_facet["@id"] == "compound/1/1/"
    assert len(compound_facet["@type"]) == 2
    assert compound_facet["formula"] == "C2 H6 O"
    assert compound_facet["casrn"] == "64-17-5"
    assert compound_facet["name"] == "ETHANOL"
    substance_facet = system["facets"][1]
    assert substance_facet["@id"] == "substance/1/1/"
    assert len(substance_facet["@type"]) == 1
    assert substance_facet["name"] == "ETHANOL"
    assert substance_facet["phase"] == "GAS"

    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material/1"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 3570 


def test_read_infrared_compressed(infrared_ethanol_compressed_file):
    scidata_dict = jcamp.read_jcamp(infrared_ethanol_compressed_file.resolve())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == '$$ Begin of the data block'
    description = graph.get("description")
    assert "JCAMP-DX" in description

    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    assert len(methodology["aspects"]) == 0 

    system = scidata_dict["@graph"]["scidata"]["system"]
    assert len(system["facets"]) == 0 

    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material/1"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 1970 


@pytest.mark.skip("Broken test due to SciDataLib not handling jcamp 'children'")
def test_read_infrared_compound(infrared_compound_file):
    scidata_dict = jcamp.read_jcamp(infrared_compound_file.resolve())


def test_read_infrared_multiline(infrared_multiline_file):
    scidata_dict = jcamp.read_jcamp(infrared_multiline_file.resolve())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == 'multiline datasets test'
    assert graph['publisher'] == 'Origin test'
    description = graph.get("description")
    assert "JCAMP-DX" in description

    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    assert len(methodology["aspects"]) == 2 
    aspects = methodology["aspects"]
    assert len(aspects[0]["settings"]) == 1 
    assert aspects[0]["settings"][0]["value"]["number"] == 32.0

    system = scidata_dict["@graph"]["scidata"]["system"]
    assert len(system["facets"]) == 0 

    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material/1"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 1919 


def test_read_mass(mass_ethanol_file):
    scidata_dict = jcamp.read_jcamp(mass_ethanol_file.resolve())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == 'ethanol'
    assert graph['publisher'] == 'Widener University'
    description = graph.get("description")
    assert "JCAMP-DX" in description

    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    assert len(methodology["aspects"]) == 1 
    aspects = methodology["aspects"]
    assert aspects[0]["instrument"] == "NIST Database"

    system = scidata_dict["@graph"]["scidata"]["system"]
    assert len(system["facets"]) == 0 

    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material/1"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 12 


def test_read_neutron(neutron_emodine_file):
    scidata_dict = jcamp.read_jcamp(neutron_emodine_file.resolve())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == "Emodine, C15H10O4"
    assert graph['publisher'] == 'TFXA, ISIS'
    description = graph.get("description")
    assert "JCAMP-DX" in description

    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    assert len(methodology["aspects"]) == 1 

    system = scidata_dict["@graph"]["scidata"]["system"]
    assert len(system["facets"]) == 0 

    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material/1"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 1992 


def test_read_uvvis(uvvis_toluene_file):
    scidata_dict = jcamp.read_jcamp(uvvis_toluene_file.resolve())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == "Toluene"
    assert graph['publisher'] == 'INSTITUTE OF ENERGY PROBLEMS OF CHEMICAL PHYSICS, RAS'
    description = graph.get("description")
    assert "JCAMP-DX" in description

    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    assert len(methodology["aspects"]) == 1 

    system = scidata_dict["@graph"]["scidata"]["system"]
    assert len(system["facets"]) == 1

    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material/1"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 335 


def test_read_raman(raman_tannic_acid_file):
    scidata_dict = jcamp.read_jcamp(raman_tannic_acid_file.resolve())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == 'tannic acid'
    assert graph['publisher'] == 'Ocean Optics R2000'

    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    assert len(methodology["aspects"]) == 1

    # System
    system = scidata_dict["@graph"]["scidata"]["system"]
    assert len(system.get("facets")) == 0

    # Dataset
    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material/1"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 1949 


def test_write_raman(tmp_path, raman_tannic_acid_file):
    scidata_dict = jcamp.read_jcamp(raman_tannic_acid_file.resolve())
    jcamp_dir = tmp_path / "jcamp"
    jcamp_dir.mkdir()
    filename = jcamp_dir / "raman_tannic_acid.jdx"

    jcamp.write_jcamp(filename.resolve(), scidata_dict)

    result = filename.read_text().splitlines()
    target = raman_tannic_acid_file.read_text().splitlines()
    skip_keys = [
        "##DATA TYPE",
        "##YUNITS",
    ]
    result = _remove_elements_from_list(result, skip_keys)
    target = _remove_elements_from_list(target, skip_keys)

    for result_element, target_element in zip(result, target):
        result_list = [x.strip() for x in result_element.split(',')]
        target_list = [x.strip() for x in target_element.split(',')]
        assert result_list == target_list
