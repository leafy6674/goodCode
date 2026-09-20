class Solution:
    def summaryRanges(self, nums: list[int]) -> list[str]:
        res = []
        n = len(nums)
        i = 0

        while i < n:
            range_start = i
            while i + 1 < n and nums[i + 1] == nums[i] + 1:
                i += 1

            if i > range_start:
                res.append(f"{nums[range_start]}->{nums[i]}")
            else:
                res.append(f"{nums[range_start]}")

            i += 1

        return res
