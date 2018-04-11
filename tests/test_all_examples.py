import unittest
import importlib
import os
import sys

def run_example( testcase, fname ):
    no_throw = True
    msg = ""
    try:
        mod = importlib.import_module(fname)
    except Exception as exc:
        msg = str(exc)
        no_throw = False
    testcase.assertTrue( no_throw, msg=msg )

class TestSequence( unittest.TestCase ):
    pass

# Get all files in the example folder
all_files = os.listdir("examples")
sys.path.append("examples")

example_files = [fname for fname in all_files if fname.startswith("ex") and fname.endswith(".py")]

for i in range(len(example_files)):
    modname = example_files[i].split(".")[0]
    testmethodname = "test_"+modname
    test_method = lambda self: run_example(self,modname)
    setattr(TestSequence, testmethodname, test_method)

if __name__ == "__main__":
    unittest.main()