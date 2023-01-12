
base64_encoding_set = {'A':0, 'B':1, 'C':2 , 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'I':8, 'J':9, 
'K':10, 'L':11, 'M':12, 'N':13, 'O':14, 'P':15, 'Q':16, 'R':17, 'S':18, 'T':19, 'U':20, 'V':21, 'W':22, 'X':23, 'Y':24, 'Z':25, 
'a':26, 'b':27, 'c':28, 'd':29, 'e':30, 'f':31, 'g':32, 'h':33, 'i':34, 'j':35, 'k':36, 'l':37, 'm':38, 'n':39, 'o':40, 'p':41, 
'q':42, 'r':43, 's':44, 't':45, 'u':46, 'v':47, 'w':48, 'x':49, 'y':50, 'z':51, '0':52, '1':53, '2':54, '3':55, '4':56, '5':57, 
'6':58, '7':59, '8':60, '9':61, '+':62, '/':63, '=':0}

def base64Decode(base64String: str) -> bytearray:
    result = bytearray()
    result_str = ''
    if base64String == None:
        return result
    _len = len(base64String)
    if _len % 4 != 0:
        print("Base64: Invalid length")
        return result
    pad = 0
    if base64String[-2] == '=' and base64String[-1] == '=':
        pad = 2
    elif base64String[-1] == '=':
        pad = 1
    for i in range(0, _len, 4):
        temp = base64_encoding_set[base64String[i]] << 18
        temp |= (base64_encoding_set[base64String[i+1]] << 12)
        temp |= (base64_encoding_set[base64String[i+2]] << 6)
        temp |= base64_encoding_set[base64String[i+3]]
        result_str += chr((temp & 0xff0000) >> 16)
        result_str += chr((temp & 0xff00) >> 8)
        result_str += chr((temp & 0xff))
    
    if pad == 2:
        result_str = result_str[:-2]
    elif pad == 1:
        result_str = result_str[:-1]
    result = bytearray(result_str, "utf-8")
    print("Decoded string is ", result_str, "and len is ", len(result_str))
    return result

if __name__ == '__main__':
    result = base64Decode("YWE=")
    print(result)
