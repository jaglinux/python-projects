def unique_num(a):
    write_index=0
    if not a:
        return write_index
    if len(a) == 1:
        return 1

    for i in range(1, len(a)):
        if a[i] != a[i-1]:
            write_index+=1

    return write_index+1


b = [1,2,2,3,3,7,7,7,8]
result = unique_num(b)
print(result)
# 5

# time complexity is O(n)
# Space complexity is 1
