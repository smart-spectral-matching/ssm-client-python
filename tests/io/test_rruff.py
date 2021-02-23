import pathlib
import pytest

from ssm_rest_python_client.io import rruff, scidata
from tests import TEST_DATA_DIR


@pytest.fixture
def raman_soddyite_file():
    """
    Raman RRUFF file for Soddyite for wavelength 780 nm
    Retrieved on 1/12/2021 from:
        https://rruff.info/tmp_rruff/Soddyite__R060361__Broad_Scan__780__0__unoriented__Raman_Data_RAW__21504.rruff  # noqa: E501
    """
    p = pathlib.Path(TEST_DATA_DIR, "rruff", "raman_soddyite.rruff")
    return p


def test_read_rruff(raman_soddyite_file):
    scidata_dict = rruff.read_rruff(raman_soddyite_file.absolute())
    defaults = scidata.get_scidata_defaults()

    # Top-level section
    graph = scidata_dict["@graph"]
    assert graph["@id"] == ""
    assert graph["@type"] == defaults["@graph"]["@type"]
    assert graph["title"] == "Soddyite"
    assert graph["uid"] == "rruff:R060361"

    assert len(graph["author"]) == 1
    assert graph["author"][0]["name"] == "Michael Scott"

    assert len(graph["sources"]) == 2
    assert graph["sources"][0]["@type"] == "dc:source"
    assert "Mineralogical" in graph["sources"][0]["citation"]
    assert graph["sources"][0]["reftype"] == "journal article"
    assert graph["sources"][0]["doi"] == "10.1515/9783110417104-003"

    assert graph["sources"][1]["@type"] == "dc:source"
    assert "RRUFF" in graph["sources"][1]["citation"]
    assert graph["sources"][1]["url"] == "https://rruff.info/R060361"

    # Check description has all the keywords from RRUFF file
    description = graph.get("description")
    for rruff_keyword in ["DESCRIPTION", "LOCALITY", "STATUS"]:
        assert rruff_keyword in description

    # Check that the DESCRIPTION from RRUFF file is copied over
    for description_keyword in ["pyramidal", "malachite", "brochantite"]:
        assert description_keyword in description

    # Check that the LOCALITY from RRUFF file is copied over
    for locality_keyword in ["Musonoi", "Kolwezi", "Shaba", "Zaire"]:
        assert locality_keyword in description

    # Check that the STATUS from RRUFF file is copied over
    for status_keyword in ["identification", "single-crystal", "X-ray"]:
        assert status_keyword in description

    # Methodology
    methodology = scidata_dict["@graph"]["scidata"]["methodology"]
    target = defaults["@graph"]["scidata"]["methodology"]
    assert methodology["@id"] == target["@id"]
    assert methodology["@type"] == target["@type"]
    assert len(methodology["evaluation"]) == 1
    assert methodology["evaluation"] == ["experimental"]
    assert len(methodology["aspects"]) == 1
    aspects = methodology["aspects"]
    assert len(aspects[0]["settings"]) == 1
    assert aspects[0]["settings"][0]["value"]["number"] == 780

    # System
    system = scidata_dict["@graph"]["scidata"]["system"]
    target = defaults["@graph"]["scidata"]["system"]
    assert system["@id"] == target["@id"]
    assert system["@type"] == target["@type"]
    assert system["discipline"] == "w3i:Chemistry"
    assert system["subdiscipline"] == "w3i:AnalyticalChemistry"
    assert len(system["facets"]) == 1
    facet = system["facets"][0]
    assert facet["@id"] == "material/1/"
    assert len(facet["@type"]) == 2
    assert facet["materialType"] == "(UO_2_)_2_SiO_4_&#183;2H_2_O"
    assert facet["name"] == "Soddyite"

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
    assert attributes[0]["value"]["number"] == "2444"
    assert attributes[1]["property"] == "First X-axis Value"
    assert attributes[1]["value"]["number"] == "107.9252"
    assert attributes[2]["property"] == "Last X-axis Value"
    assert attributes[2]["value"]["number"] == "1285.736"
    assert attributes[3]["property"] == "Minimum X-axis Value"
    assert attributes[3]["value"]["number"] == "107.9252"
    assert attributes[4]["property"] == "Maximum X-axis Value"
    assert attributes[4]["value"]["number"] == "1285.736"
    assert attributes[5]["property"] == "First Y-axis Value"
    assert attributes[5]["value"]["number"] == "831.4121"
    assert attributes[6]["property"] == "Last Y-axis Value"
    assert attributes[6]["value"]["number"] == "66.16613"
    assert attributes[7]["property"] == "Minimum Y-axis Value"
    assert attributes[7]["value"]["number"] == "61.52692"
    assert attributes[8]["property"] == "Maximum Y-axis Value"
    assert attributes[8]["value"]["number"] == "3246.546"
    assert attributes[9]["property"] == "X-axis Scaling Factor"
    assert attributes[9]["value"]["number"] == "1"
    assert attributes[10]["property"] == "Y-axis Scaling Factor"
    assert attributes[10]["value"]["number"] == "1"
