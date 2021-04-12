import random
import string

inputs_words = string.ascii_letters + string.digits + string.punctuation

n = int(input('Enter number of password required: '))
l = int(input('Enter length of password: '))

for i in range(n):
    a = random.sample(inputs_words, l)
    b = ''
    for j in range(l):
        b += random.choice(inputs_words)
    print(f" {i} password is {''.join(a)} ")
    print(f" {i} password is {b} ")
