def fib(n, H=None):
    if H is None:
        H = {}
    if n in H:
        print('hit')
        return H[n]
    elif n <= 1:
        return n
    else:
        value = fib(n-1, H) + fib(n-2, H)
        H[n] = value
        return value

print(fib(8))
# result is 21

'''
Time complexity is O(n) due to dp or else its O(2**n)
Space complexity is O(n)
Python tip: Do not use H={} in function parameter.
'''
