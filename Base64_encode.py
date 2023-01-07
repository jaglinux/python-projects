base64_encoding_set = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def ascii_to_base64(ascii: str) -> str:
    result = ""
    _len = len(ascii)
    if _len == 0:
        return result
    pad = _len % 3

    for i in range(0,_len,3):
        apply_pad = False
        block = ascii[i:i+3].encode("utf-8")
        block = int.from_bytes(block, "big")
        if i+3 > _len:
            apply_pad = True
            if pad == 1:
                block <<= 16
            else:
                block <<= 8

        print(hex(block))
        result += base64_encoding_set[block >> 18]
        result += base64_encoding_set[(block >> 12) & 0x3f]
        if apply_pad == True and pad == 1:
            return result + '=' + '='
        result += base64_encoding_set[(block >> 6) & 0x3f]
        if apply_pad == True and pad == 2:
            return result + '='
        result += base64_encoding_set[block & 0x3f]
    
    return result

result = ascii_to_base64("AAA")
print(result)
# QUFB
