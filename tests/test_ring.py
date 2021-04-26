from random_store.ringv0 import Ring


def test_pokemons(pokemons):
    assert len(pokemons) == 100
    assert isinstance(pokemons[0].get("name"), str)

def test_ring_import():
    r = Ring()
    assert isinstance(r, Ring)
