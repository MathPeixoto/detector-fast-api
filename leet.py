from typing import Optional, List


def numMostPopular(arr, length):
    counts = {}
    for i in range(length):
        if arr[i] in counts:
            counts[arr[i]] += 1
        else:
            counts[arr[i]] = 1

    max_count = 0
    most_frequent = None
    for num, count in counts.items():
        if count > max_count or (count == max_count and num < most_frequent):
            max_count = count
            most_frequent = num

    return most_frequent



if __name__ == "__main__":
    print(numMostPopular([34, 31, 34, 77, 82], 5))  # Output: 34
    print(numMostPopular([22, 101, 102, 101, 102, 525, 88], 7))  # Output: 101
    print(numMostPopular([66], 1))
