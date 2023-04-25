import pathlib

import pytest


@pytest.fixture()
def inputsdir(request):
    file = pathlib.Path(request.module.__file__)
    return file.parent / file.stem
