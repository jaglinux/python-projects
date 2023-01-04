# Inspired from https://trebaud.github.io/posts/merkle-tree/
# Used Crypto.Hash.keccak to pass Integer as raw bytes
# hashlib.sha256 works well with string as parameter.
# Crypto.Hash.keccak can be used to pass Integer or String since both can be coverted to bytes easily.

from typing import List
import typing
import hashlib
from Crypto.Hash import keccak

class Node:
    def __init__(self, left, right, value)-> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value

    @staticmethod
    def hash(val):
        keccak_hash = keccak.new(digest_bits=256)
        if isinstance(val,int):
            print("Input is ", hex(val))
            bytes_len = (len(hex(val))-2) // 2
            keccak_hash.update(val.to_bytes(bytes_len, byteorder ='big'))
        else:
            print("Input is ", val)
            keccak_hash.update(val)
        _hash = keccak_hash.digest()
        print("Hash is ", keccak_hash.hexdigest())
        return _hash

class MerkleTree:
    def __init__(self, values):
        self.__buildTree(values)

    def __buildTree(self, values):
        leaves: List[Node] = [Node(None, None, Node.hash(e)) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1:][0]) # duplicate last elem if odd number of elements
        self.root: Node = self.__buildTreeRec(leaves)

    def __buildTreeRec(self, nodes):
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            print("__buildTreeRec ", nodes[0].value, nodes[1].value, nodes[0].value + nodes[1].value)
            return Node(nodes[0], nodes[1], Node.hash(nodes[0].value + nodes[1].value))

        left: Node = self.__buildTreeRec(nodes[:half])
        right: Node = self.__buildTreeRec(nodes[half:])
        value= Node.hash(left.value + right.value)
        return Node(left, right, value)

    def printTree(self):
        self.__printTreeRec(self.root)

    def __printTreeRec(self, node):
        if node != None:
            print(node.value)
            self.__printTreeRec(node.left)
            self.__printTreeRec(node.right)

    def getRootHash(self):
        return hex(int.from_bytes(self.root.value, byteorder ='big'))

elems = [0x1aD91ee08f21bE3dE0BA2ba6918E714dA6B45836, 0x8fb3b37f83698b75d90145d8f536810ad6cdb107,
0xb5d85cbf7cb3ee0d56b3bb207d5fc4b82f43f511, 0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740]
mtree = MerkleTree(elems)
print("Merkle Root Hash is ", mtree.getRootHash())

