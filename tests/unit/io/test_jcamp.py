import pytest
from typing import List

from ssm_client.io import jcamp


def _remove_elements_from_list(
    old_list: List[str], skip_elements: List[str]
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
        element_list = [x.strip() for x in element.split(",")]
        for key in skip_elements:
            for x in element_list:
                if key in x:
                    keep = False

        if keep:
            new_list.append(element)

    return new_list


# Tests


@pytest.mark.skip(
    "Broken test due to SciDataLib not handling jcamp 'children'"
)
def test_read_hnmr(hnmr_ethanol_jcamp):
    scidata_dict = jcamp.read_jcamp(hnmr_ethanol_jcamp.resolve())
    assert scidata_dict == 0


def test_read_infrared(infrared_ethanol_jcamp):
    scidata_dict = jcamp.read_jcamp(infrared_ethanol_jcamp.resolve())

    graph = scidata_dict.get("@graph")
    assert graph["title"] == "ETHANOL"
    assert graph["publisher"] == "DOW CHEMICAL COMPANY"
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


def test_read_infrared_compressed(infrared_ethanol_compressed_jcamp):
    scidata_dict = jcamp.read_jcamp(
        infrared_ethanol_compressed_jcamp.resolve()
    )

    graph = scidata_dict.get("@graph")
    assert graph["title"] == "$$ Begin of the data block"
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


@pytest.mark.skip(
    "Broken test due to SciDataLib not handling jcamp 'children'"
)
def test_read_infrared_compound(infrared_compound_jcamp):
    scidata_dict = jcamp.read_jcamp(infrared_compound_jcamp.resolve())
    assert scidata_dict == 0


def test_read_infrared_multiline(infrared_multiline_jcamp):
    scidata_dict = jcamp.read_jcamp(infrared_multiline_jcamp.resolve())

    graph = scidata_dict.get("@graph")
    assert graph["title"] == "multiline datasets test"
    assert graph["publisher"] == "Origin test"
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


def test_read_mass(mass_ethanol_jcamp):
    scidata_dict = jcamp.read_jcamp(mass_ethanol_jcamp.resolve())

    graph = scidata_dict.get("@graph")
    assert graph["title"] == "ethanol"
    assert graph["publisher"] == "Widener University"
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


def test_read_neutron(neutron_emodine_jcamp):
    scidata_dict = jcamp.read_jcamp(neutron_emodine_jcamp.resolve())

    graph = scidata_dict.get("@graph")
    assert graph["title"] == "Emodine, C15H10O4"
    assert graph["publisher"] == "TFXA, ISIS"
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


def test_read_uvvis(uvvis_toluene_jcamp):
    scidata_dict = jcamp.read_jcamp(uvvis_toluene_jcamp.resolve())

    graph = scidata_dict.get("@graph")
    assert graph["title"] == "Toluene"
    assert (
        graph["publisher"]
        == "INSTITUTE OF ENERGY PROBLEMS OF CHEMICAL PHYSICS, RAS"
    )
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


def test_read_raman(raman_tannic_acid_jcamp):
    scidata_dict = jcamp.read_jcamp(raman_tannic_acid_jcamp.resolve())

    graph = scidata_dict.get("@graph")
    assert graph["title"] == "tannic acid"
    assert graph["publisher"] == "Ocean Optics R2000"

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


def test_write_raman(tmp_path, raman_tannic_acid_jcamp):
    scidata_dict = jcamp.read_jcamp(raman_tannic_acid_jcamp.resolve())
    jcamp_dir = tmp_path / "jcamp"
    jcamp_dir.mkdir()
    filename = jcamp_dir / "raman_tannic_acid.jdx"

    jcamp.write_jcamp(filename.resolve(), scidata_dict)

    result = filename.read_text().splitlines()
    target = raman_tannic_acid_jcamp.read_text().splitlines()
    skip_keys = [
        "##DATA TYPE",
        "##YUNITS",
    ]
    result = _remove_elements_from_list(result, skip_keys)
    target = _remove_elements_from_list(target, skip_keys)

    for result_element, target_element in zip(result, target):
        result_list = [x.strip() for x in result_element.split(",")]
        target_list = [x.strip() for x in target_element.split(",")]
        assert result_list == target_list
