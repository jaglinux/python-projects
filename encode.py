a = ['gfg', 'is', 'best']

ascii_map = {
    'a': 97,
    'b': 98,
    'c': 99,
    'd': 100,
    'e': 101,
    'f': 102,
    'g': 103,
    'h': 104,
    'i': 105,
    'j': 106,
    'k': 107,
    'l': 108,
    'm': 109,
    'n': 110,
    'o': 111,
    'p': 112,
    'q': 113,
    'r': 114,
    's': 115,
    't': 116,
    'u': 117,
    'v': 118,
    'w': 119,
    'x': 120,
    'y': 121,
    'z': 122,
}

def convert_string_to_ascii(a):
    output = []
    for i in a:
        for j in i:
            output.append(ord(j))
    print(output)
    return output

def convert_string_to_ascii_with_logic(a):
    output=[]
    for i in a:
        for j in i:
            value = ascii_map.get(j)
            if  value is not None:
                output.append(value)
            else:
                print("no mapping found")
    print(output)
    return output

out_1 = convert_string_to_ascii(a)
out_2 = convert_string_to_ascii_with_logic(a)
assert out_1 ==  out_2, "Not a match"
