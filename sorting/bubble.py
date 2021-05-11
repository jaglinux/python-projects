def bubble(a):
    for i in range(len(a)):
        for j in range(len(a)-i-1):
            if a[j] > a[j+1]:
                a[j], a[j+1] = a[j+1], a[j]

b = [64, 34, 25, 12, 22, 11, 90]
bubble(b)
print(b)
#[11, 12, 22, 25, 34, 64, 90]

# time complexity is O(n**2)
# space complexity is O(1)
