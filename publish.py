"""
Automatically publishing to pypi.
"""

import wexpect

def main():
    setupfile = "setup.py"
    child = wexpect.spawn("py", args=[setupfile, "sdist"])
    print(child.read())
    #child = wexpect.spawn("twine", args=["upload", "dist/*"])
    #print(child.read())

if __name__ == "__main__":
    main()
