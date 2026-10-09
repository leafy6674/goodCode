class Solution:
    def rightRotate(self, s: str, k: int) -> str:
        if not s:
            return s

        k %= len(s)
        return s[-k:] + s[:-k]
