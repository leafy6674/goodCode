class Solution:
    def digitSquareSum(self, n: int) -> int:
        _sum = 0
        while n > 0:
            last = n % 10
            n //= 10
            _sum += last * last
        return _sum

    def isHappy(self, n: int) -> bool:
        seen = set()
        while n != 1:
            if n in seen:
                return False  # revisited a number: stuck in a cycle
            seen.add(n)
            n = self.digitSquareSum(n)
        return True
