import sys
import os

# Add src to the path to support running out-of-the-box
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from synthetic_txn_generator.main import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
