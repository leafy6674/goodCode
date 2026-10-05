class Solution:
    def replaceNumber(self, s: str) -> str:
        result = []

        for ch in s:
            if ch.isdigit():
                result.append("number")
            else:
                result.append(ch)

        return "".join(result)
