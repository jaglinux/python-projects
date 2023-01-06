from typing import List
import typing
import hashlib
from Crypto.Hash import keccak

class Node:
    def __init__(self, left, right, value)-> None:
        self.left = left
        self.right = right
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
    def __init__(self, elems):
        self.tree = []
        leaves_level = [Node(None, None, Node.hash(elem)) for elem in elems]
        if len(leaves_level) % 2 == 1:
            leaves_level.append(leaves_level[-1:][0])
        self.tree.append(leaves_level)
        self.build_rest_of_tree()

    def build_rest_of_tree(self):
        prev_index = len(self.tree) - 1 
        leaves_level = []
        for i in range(0,len(self.tree[prev_index]), 2):
            leaves_level.append(Node(self.tree[prev_index][i], self.tree[prev_index][i+1], 
                Node.hash(self.tree[prev_index][i].value+self.tree[prev_index][i+1].value)))
        if len(leaves_level) == 1:
            self.tree.append(leaves_level)
            return
        if len(leaves_level) % 2 == 1:
            leaves_level.append(leaves_level[-1:][0])
        self.tree.append(leaves_level)
        self.build_rest_of_tree()
        
    def print_tree(self):
        i=0
        for level in self.tree:
            print("Level -------   ", i, " ----------")
            for element in level:
                print(element.left, element.right, hex(int.from_bytes(element.value, byteorder="big")))
            i+=1
    
    def print_root(self):
        print("Root value is ", hex(int.from_bytes(self.tree[len(self.tree)-1][0].value, byteorder="big")))

elems = [0x1aD91ee08f21bE3dE0BA2ba6918E714dA6B45836, 0x8fb3b37f83698b75d90145d8f536810ad6cdb107,
0xb5d85cbf7cb3ee0d56b3bb207d5fc4b82f43f511, 0xddfabcdc4d8ffc6d5beaf154f18b778f892a0740]
m = MerkleTree(elems)
m.print_tree()
m.print_root()
