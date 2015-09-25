from server_check import bcolors


def test_00_error():
    output = bcolors.error("test")
    assert ' ERROR ' in output
    assert 'test' in output


def test_01_warning():
    output = bcolors.warning("test")
    assert 'WARNING' in output
    assert 'test' in output


def test_02_ok():
    output = bcolors.ok("test")
    assert ' OK ' in output
    assert 'test' in output


def test_03_header():
    output = bcolors.header("test")
    assert 'Checking' in output
    assert 'test' in output
