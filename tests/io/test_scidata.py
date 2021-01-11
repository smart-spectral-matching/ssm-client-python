from ssm_rest_python_client.io import scidata


def test_get_context_header():
    header = scidata._get_context_header()
    assert '@context' in header
    assert len(header.get('@context')) == 2


def test_get_scidata_base():
    scidata_dict = scidata.get_scidata_base()
    assert '@context' in scidata_dict
    assert len(scidata_dict.get('@context')) == 2

    assert 'generatedAt' in scidata_dict
    generated_time = scidata_dict.get('generatedAt')
    assert len(generated_time.split('-')) == 3
    assert len(generated_time.split(':')) == 3

    assert 'version' in scidata_dict
    assert scidata_dict.get('version') == 2

    assert '@id' in scidata_dict
    assert not scidata_dict.get('@id')

    assert '@graph' in scidata_dict
    graph = scidata_dict.get('@graph')
    assert '@id' in graph
    assert not graph.get('@id')
    assert '@type' in graph
    assert graph.get('@type') == "sdo:scidataFramework"
