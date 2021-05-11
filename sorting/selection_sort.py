def selection(a):
    for i in range(len(a)-1):
        minimum_index = i
        for j in range(i, len(a)):
            if a[j] < a[minimum_index]:
                minimum_index = j
        a[i], a[minimum_index] = a[minimum_index], a[i]


b = [7,4,10,8,3,1]
selection(b)
print(b)
#[1, 3, 4, 7, 8, 10]

# time complexity is O(n**2)
# space complexity is O(1)
