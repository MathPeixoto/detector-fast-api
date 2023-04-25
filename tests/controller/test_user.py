from src.controller.user import root


class TestUser:
    def test_root(self):
        assert root() == "Hello World"  # add assertion here
