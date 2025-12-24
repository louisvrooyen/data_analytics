# test_cleanup.py

import sys
from cleaning_logic import clean_str_name, clean_suburb

def main():
    if len(sys.argv) < 3:
        print("Usage: python test_cleanup.py type value")
        print("type: str | suburb")
        print("Example:")
        print('  python test_cleanup.py str "(m10) modderdam road"')
        sys.exit(1)

    mode = sys.argv[1].lower()
    value = " ".join(sys.argv[2:])

    if mode == "str":
        clean_str_name(value)
    elif mode == "suburb":
        clean_suburb(value)
    else:
        print("Unknown type. Use 'str' or 'suburb'.")
        sys.exit(1)

if __name__ == "__main__":
    main()