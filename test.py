import json
from binascii import crc32
from collections import Counter
from pprint import pprint
from typing import Dict, List

from random_store.ring import Node, Ring


def open_pokemons(path_file: str) -> List[Dict]:
    """ Open a file with json data about pokemons """
    with open(path_file, 'r') as f:
        pokemons = []
        for line in f.readlines():
            pokemons.append(json.loads(line.strip()))
    return pokemons


def load(key: str, ring: Ring, mt: Dict, replicas=2):
    # hash_key = f"{crc32(key.encode()):x}"
    assert len(ring.nodes) >= replicas
    _nodes = ring.lookup(key)[:replicas]
    # addresses = ",".join([n[1].addr for n in _nodes])
    addresses = [n[1].addr for n in _nodes]
    mt.update({key: addresses})


def calculate_balance(data: Dict):
    servers = dict()
    c = Counter()
    for k, v in data.items():
        srv1 = v[0]
        srv2 = v[1]
        if servers.get(srv1):
            servers[srv1].append(k)
        else:
            servers.update({srv1: [k]})
        c.update(srv1)

        if servers.get(srv2):
            servers[srv2].append(k)
        else:
            servers.update({srv2: [k]})

        c.update(srv2)

    return servers, c


def per_server(data):
    """
    Counts elements by server
    """
    _servers = dict()
    _c = Counter()
    t = 0
    for k, v in data.items():
        _c.update(v)
        for srv in v:
            if _servers.get(srv):
                _servers[srv].append(k)
            else:
                _servers.update({srv: [k]})
        # for
        # srv.update(v)
        t += len(v)

    return _servers, _c, t


def calculate_destinations(pokes, ring):
    c = Counter()
    for x in range(0, 10):
        destiny = ring.lookup(pokes[x]['name'])[:2]
        print(
            f"for pokemon {pokemons[x]['name']}\t\tA:{destiny[0][1].addr} B:{destiny[1][1].addr}")

        c.update(destiny[0][1].addr)
        c.update(destiny[1][1].addr)

    return c


def sum_counter(c):
    total = 0
    for k in c.keys():
        total += c[k]

    return total


def print_memtable(mt):
    for k, v in mt.items():
        print(f'for {k}\t\t{v}')


def rebalance(servers: Dict, srv: str, r: Ring, mtable: Dict, replicas=2):
    """ only for downgrade """
    keys = servers[srv]
    for k in keys:
        options = r.lookup(k)[:replicas]

        addresses = [n[1].addr for n in options]
        mtable.update({k: addresses})

        for dst in options:
            # print(f"Destiny for {k}: {dst}")
            # _new_keys = list(servers[dst[1].addr)
            if k not in servers[dst[1].addr]:
                servers[dst[1].addr].append(k)
            # else:
            #    print(f'{k} already exist in {dst[1].addr}')

        # print(dst)
    del(servers[srv])
    # print(f'Server {srv}, deleted.')
    print(f'keys {keys} from server {srv} migrated.')


if __name__ == '__main__':

    pokemons = open_pokemons("pokemons.txt")

    _REPLICAS = 3
    # Nodes creation
    nodes = [Node(str(x), f'alias-{x}') for x in range(1, 5)]
    print(f"Total nodes: {len(nodes)}")
    r = Ring(nodes)
    # nodes_counter = calculate_destinations(pokemons, r)
    # print(nodes_counter)
    # t = sum_counter(nodes_counter)
    # print(f"Total of elements: {t}")

    # keys table
    # Each word mapped to n servers
    memtable = {}
    for x in range(0, 10):
        load(pokemons[x]['name'], r, memtable, _REPLICAS)
    print("Memtable: ")
    pprint(memtable)
    print_memtable(memtable)
    servers, srv_count, srv_stats = per_server(memtable)
    print("Servers:")
    pprint(servers)
    print(f'Servers count: {srv_count}, total: {srv_stats}')

    # s, srv_counter = calculate_balance(memtable)
    # print('servers:')
    # pprint(s)
    # print(f'servers counter: {srv_counter}\n')

    print("==== REBALANCE ===")
    _srv = nodes[2].addr
    r.remove(nodes[2])
    rebalance(servers, _srv, r, memtable, replicas=_REPLICAS)
    pprint(servers)
    servers2, count2, stats2 = per_server(memtable)
    print(f'Servers count: {count2}, total: {stats2}')
    # print("SERVER 2:")
    # pprint(servers2)
    # nodes_counter2 = calculate_destinations(pokemons, r)
    # print(nodes_counter2)
    # t = sum_counter(nodes_counter2)
    # print(t)
    pprint(memtable)

    print("==== Recalculated ===")
    s, srv_counter = calculate_balance(memtable)
    print('servers:')
    pprint(s)
    print(f'servers counter: {srv_counter}\n')
