# TODO either use a python lib to solve this or make a new "version" dataclass
# this is too sloppy to use long-term and is only a temp fix

def version_str_to_tuple(s: str) -> tuple:
    nums = s.lstrip("v").split(".")
    nums = list(map(int, nums))

    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)

def version_tuple_to_str(t: tuple) -> str:
    s = ""
    for n in t:
        s += f"{str(n)}."
    s = s.rstrip(".")

    if "2.9.9" in s:
        raise ValueError
    return s
