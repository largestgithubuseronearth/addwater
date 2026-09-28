import pytest
from addwater import Application
from addwater.cli import CliProvider, CliStatus, CliException

def test_cli(request):
    assert Application(["addwater", "-h"]).run(sys.argv) == 0

def
