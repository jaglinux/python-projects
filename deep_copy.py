import copy

class Node:
    def __init__(self, val):
        self.a = val
        self.b = val+1

l1 = [Node(5), Node(10)]

l2 = copy.deepcopy(l1[-1:])

l1[1].a = 35
l1[1].b = 36

print(l1[0].a, l1[0].b, l1[1].a, l1[1].b)
print(l2[0].a, l2[0].b)
