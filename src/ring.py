import binascii
import math
from collections import defaultdict
from typing import List, Optional

# general doc
# https://medium.com/@dgryski/consistent-hashing-algorithmic-tradeoffs-ef6b8e2fcae8
# https://blog.acolyer.org/2016/03/21/maglev-a-fast-and-reliable-software-network-load-balancer/


# https://en.wikipedia.org/wiki/Rendezvous_hashing
def int_to_float(value: int) -> float:
    """Converts a uniformly random [[64-bit computing|64-bit]]
    integer to uniformly random floating point number on interval <math>[0, 1)</math>.
    """
    fifty_three_ones = 0xFFFFFFFFFFFFFFFF >> (64 - 53)
    fifty_three_zeros = float(1 << 53)
    return (value & fifty_three_ones) / fifty_three_zeros


class RendezvousHash(object):
    """
    https://github.com/ewdurbin/clandestined-python
    """

    def __init__(self, nodes=None, seed=0):
        self.nodes = []
        self.seed = seed
        if nodes is not None:
            self.nodes = nodes
        # self.hash_function = lambda x: murmur3.murmur3_32(x, seed)
        self.hash_function = lambda x: binascii.crc32(x.encode())

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
        else:
            raise ValueError("No such node %s to remove" % (node))

    def find_node(self, key):
        high_score = -1
        winner = None
        for node in self.nodes:
            score = self.hash_function("%s-%s" % (str(node), str(key)))
            if score > high_score:
                (high_score, winner) = (score, node)
            elif score == high_score:
                (high_score, winner) = (score, max(str(node), str(winner)))
        return winner


class Cluster(object):

    def __init__(self, cluster_config=None, replicas=2, seed=0):
        self.seed = seed

        def RendezvousHashConstructor():
            return RendezvousHash(nodes=None, seed=self.seed)

        self.replicas = replicas
        self.nodes = {}
        self.zones = []
        self.zone_members = defaultdict(list)
        self.rings = defaultdict(RendezvousHashConstructor)

        if cluster_config is not None:
            for node, node_data in cluster_config.items():
                name = node_data.get('name', None)
                zone = node_data.get('zone', None)
                self.add_node(node, node_name=name, node_zone=zone)

    def add_zone(self, zone):
        if zone not in self.zones:
            self.zones.append(zone)
            self.zones = sorted(self.zones)

    def remove_zone(self, zone):
        if zone in self.zones:
            self.zones.remove(zone)
            for member in self.zone_members[zone]:
                self.nodes.remove(member)
            self.zones = sorted(self.zones)
            del self.rings[zone]
            del self.zone_members[zone]
        else:
            raise ValueError("No such zone %s to remove" % (zone))

    def add_node(self, node_id, node_zone=None, node_name=None):
        if node_id in self.nodes.keys():
            raise ValueError('Node with name %s already exists', node_id)
        self.add_zone(node_zone)
        self.rings[node_zone].add_node(node_id)
        self.nodes[node_id] = node_name
        self.zone_members[node_zone].append(node_id)

    def remove_node(self, node_id, node_name=None, node_zone=None):
        self.rings[node_zone].remove_node(node_id)
        del self.nodes[node_id]
        self.zone_members[node_zone].remove(node_id)
        if len(self.zone_members[node_zone]) == 0:
            self.remove_zone(node_zone)

    def node_name(self, node_id):
        return self.nodes.get(node_id, None)

    def find_nodes(self, key, offset=None):
        nodes = []
        if offset is None:
            offset = sum(ord(char) for char in key) % len(self.zones)
        for i in range(self.replicas):
            zone = self.zones[(i + offset) % len(self.zones)]
            ring = self.rings[zone]
            nodes.append(ring.find_node(key))
        return nodes

    def find_nodes_by_index(self, partition_id, key_index):
        offset = int(partition_id) + int(key_index) % len(self.zones)
        key = "%s-%s" % (partition_id, key_index)
        return self.find_nodes(key, offset=offset)


# https://github.com/nikhilgarg28/rendezvous/blob/master/_rendezvous.py
def weight(node, key):
    """Return the weight for the key on node.
    Uses the weighing algorithm as prescibed in the original HRW white paper.
    @params:
        node : 32 bit signed int representing IP of the node.
        key : string to be hashed.
    """
    a = 1103515245
    b = 12345
    _hash = binascii.crc32(key)
    return (a * ((a * node + b) ^ _hash) + b) % (2 ^ 31)


class Node:
    """ Node abstraction """

    def __init__(self, addr: str, alias: str):
        self._addr = addr
        self._alias = alias
        self._hash = binascii.crc32(addr.encode())

    @property
    def hash(self):
        return self._hash

    def __eq__(self, other):
        return self.hash == other.hash


class Ring:
    """A ring of nodes supporting rendezvous hashing based node selection."""

    def __init__(self, nodes: Optional[List[Node]] = None):
        nodes = nodes or {}
        self._nodes = set(nodes)

    def add(self, node):
        self._nodes.add(node)

    # @staticmethod
    # def score(key: bytes, weight: int = 1):
    #    _hash = binascii.crc32(key)
    #    _hash_f = int_to_float(_hash)
    #    # score = 1.0 / -math.log(_hash_f)
    #    # return weight * score

    @property
    def nodes(self):
        return self._nodes

    def remove(self, node):
        self._nodes.remove(node)

    def lookup(self, key: str):
        """Return the node to which the given key hashes to."""
        assert len(self._nodes) > 0

        key_hash = binascii.crc32(key.encode())

        # weights = []
        # for node in self._nodes:
        #    # Should be previously calculated
        #    # nhash = binascii.crc32(node.encode())
        #    mhash = xorshiftMult64(khash ^ node.hash)
        #    weights.append((mhash, node))

        # calculates the weigth of each hashd key + node precomputed hash
        weights = [(xorshiftMult64(key_hash ^ node.hash))
                   for node in self._nodes]

        return sorted(weights)

    def __str__(self):
        return str(self.nodes)


def xorshiftMult64(x: int) -> int:
    x ^= x >> 12
    x ^= x << 25
    x ^= x >> 27
    return x * 2685821657736338717
