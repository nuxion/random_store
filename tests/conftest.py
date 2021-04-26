import json
from typing import Dict, List

import pytest


def open_pokemons(path_file: str) -> List[Dict]:
    """ Open a file with json data about pokemons
    This file is used as a predictible data input
    for the store
    """
    with open(path_file, 'r') as f:
        pokemons = []
        for line in f.readlines():
            pokemons.append(json.loads(line.strip()))
    return pokemons


@pytest.fixture(scope='module')
def pokemons():
    _pokemons = open_pokemons("tests/pokemons.txt")

    yield _pokemons
