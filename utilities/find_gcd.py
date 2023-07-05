import math
from typing import List


def find_gcd(numbers: List):
    """
    求最大公约数
    """
    num1 = numbers[0]
    num2 = numbers[1]
    gcd = math.gcd(num1, num2)

    for i in range(2, len(numbers)):
        gcd = math.gcd(gcd, numbers[i])

    return gcd


if __name__ == '__main__':
    numbers = [8, 12, 24, 36, ]  # 可以是任意个数的列表
    print(find_gcd(numbers))  # 输出最大公约数
