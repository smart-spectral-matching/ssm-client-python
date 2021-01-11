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
