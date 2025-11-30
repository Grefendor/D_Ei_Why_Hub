import pytest
import sys
import os

def run_tests():
    """
    Runs all tests in the directory where this script resides using pytest.
    """
    print("Running Comprehensive Test Suite...")
    
    # Determine the directory of this script (tests directory)
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Determine project root (parent of tests directory)
    project_root = os.path.dirname(tests_dir)
    
    # Add project root to python path so src modules can be imported
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Arguments for pytest
    # We point pytest to the tests_dir to ensure it finds tests regardless of CWD
    args = [
        tests_dir,
        "-v",  # Verbose
    ]
    
    # Run tests
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\nAll tests passed successfully!")
    else:
        print(f"\nTests failed with exit code {exit_code}.")
        
    sys.exit(exit_code)

if __name__ == "__main__":
    run_tests()
