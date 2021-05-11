def add(a):
    carry = 1
    result = []
    for i in reversed(a):
        print(i)
        if carry:
            i+=1
        carry = 0
        if i >= 10:
            carry = 1
        result.append(i%10)

    if carry == 1:
        result[-1]+=1

    return list(reversed(result))

result1 = add([1,1,1,9])
print(result1)
# [1, 1, 2, 0]
# time complexity is O(n)
# space complexity is O(n) if we consider result
