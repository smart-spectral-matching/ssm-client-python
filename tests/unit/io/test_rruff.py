from ssm_client.io import rruff
from tests import TEST_DATA_DIR


def test_read_rruff(raman_soddyite_rruff):
    scidata_dict = rruff.read_rruff(raman_soddyite_rruff.absolute())

    graph = scidata_dict.get('@graph')
    assert graph['title'] == 'Soddyite'
    assert graph['publisher'] == 'RRUFF'
    assert graph["uid"] == "rruff:R060361"
    assert "sources" in graph
    sources = graph["sources"]
    assert len(sources) == 2
    assert sources[0]["@type"] == "dc:source"
    assert "Mineralogical" in sources[0]["citation"]
    assert sources[0]["reftype"] == "journal article"
    assert sources[0]["doi"] == "10.1515/9783110417104-003"
    assert sources[1]["@type"] == "dc:source"
    assert "RRUFF" in sources[1]["citation"]
    assert sources[1]["url"] == "https://rruff.info/R060361"
    description = graph.get("description")
    for rruff_keyword in ["DESCRIPTION", "LOCALITY", "STATUS"]:
        assert rruff_keyword in description
    for description_keyword in ["pyramidal", "malachite", "brochantite"]:
        assert description_keyword in description
    for locality_keyword in ["Musonoi", "Kolwezi", "Shaba", "Zaire"]:
        assert locality_keyword in description
    for status_keyword in ["identification", "single-crystal", "X-ray"]:
        assert status_keyword in description

    methodology = graph.get("scidata").get("methodology")
    assert "aspects" in methodology
    aspects = methodology.get("aspects")
    assert len(aspects) == 1 
    assert "settings" in aspects[0]
    settings = aspects[0].get("settings")
    assert len(settings) == 1 
    wavelength = settings[0].get("value").get("number")
    assert wavelength == 780

    system = scidata_dict.get("@graph").get("scidata").get("system")
    assert "facets" in system
    assert len(system.get("facets")) == 1 
    material_facet = system["facets"][0]
    assert material_facet["@id"] == "material/1/"
    assert len(material_facet["@type"]) == 12
    assert material_facet["name"] == "Soddyite"
    assert material_facet["materialType"] == "(UO_2_)_2_SiO_4_&#183;2H_2_O"

    dataset = scidata_dict.get("@graph").get("scidata").get("dataset")
    assert len(dataset) == 5
    assert "scope" in dataset
    assert dataset["scope"] == "material"
    assert "datagroup" in dataset
    assert "dataseries" in dataset
    dataseries_0 = dataset.get("dataseries")[0]
    assert "parameter" in dataseries_0
    assert len(dataseries_0.get("parameter")) == 2
    parameter_0 = dataseries_0.get("parameter")[0]
    assert len(parameter_0) == 9
    assert "dataarray" in parameter_0
    assert len(parameter_0.get("dataarray")) == 2444 


def test_write_rruff(tmp_path, raman_soddyite_rruff):
    scidata_dict = rruff.read_rruff(raman_soddyite_rruff.absolute())
    rruff_dir = tmp_path / "rruff"
    rruff_dir.mkdir()
    filename = rruff_dir / "raman_soddyite.rruff"
    rruff.write_rruff(filename.absolute(), scidata_dict)
    result = filename.read_text().splitlines()
    target = raman_soddyite_rruff.read_text().splitlines()

    for result_element, target_element in zip(result, target):
        result_list = [x.strip() for x in result_element.split(',')]
        target_list = [x.strip() for x in target_element.split(',')]
        assert result_list == target_list
