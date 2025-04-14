
def bubblesort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr
test_cases = [
    ([2, 0, 3, 4, 5],),  
    ([5, 4, 3, 2, 1],),
    ([3, 1, 4, 1, 5, 9, 2],),
    ([4, 2, 2, 8, 3, 3, 1],),
    ([42],),
    ([],)
]


