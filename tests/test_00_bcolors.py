from server_check.bcolors import header, ok, warning, error


def test_00_error():
    output = error("test")
    assert ' ERROR ' in output
    assert 'test' in output


def test_01_warning():
    output = warning("test")
    assert 'WARNING' in output
    assert 'test' in output


def test_02_ok():
    output = ok("test")
    assert ' OK ' in output
    assert 'test' in output


def test_03_header():
    output = header("test")
    assert 'Checking' in output
    assert 'test' in output
