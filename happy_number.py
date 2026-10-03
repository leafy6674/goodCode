class Solution:
    def digitSquareSum(self, n: int) -> int:
        return sum(int(i)**2 for i in str(n))

    def isHappy(self, n: int) -> bool:
        seen = set()
        while n != 1:
            if n in seen:
                return False  # revisited a number: stuck in a cycle
            seen.add(n)
            n = self.digitSquareSum(n)
        return True
