
def grid(i, j, dp=None):
    if dp is None:
        dp = {}

    hash_val_0 = hash((i,j))
    hash_val_1 = hash((j,i))

    if hash_val_0 in dp or hash_val_1 in dp:
        return dp[hash_val_0]
    if i == 0 or j == 0:
        return 0
    if i == 1 and j == 1:
        return 1

    temp = grid(i-1, j, dp) + grid(i , j-1, dp)
    dp[hash_val_0] = dp[hash_val_1] = temp
    return temp

print(grid(18,18))

# answer is 2333606220
# time complexity O(m*n)
# space complexity O(m+n)
