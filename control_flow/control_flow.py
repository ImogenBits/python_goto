import sys
import nop

file = sys.modules["__main__"].__file__ or ""

sys.modules["control_flow"] = nop

with open(file, "r") as file:
    content = file.read()
    new = content.replace("1", "2")
    exec(new)
    raise SystemExit

