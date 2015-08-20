class TestException(Exception):
    def __init__(self, arg):
        self.message = arg
