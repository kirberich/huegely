import sys
import os

# This is obviously not the right way to set up things, but I cannot be bothered to figure 
# out how to run the tests without tox otherwise.
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(1,os.path.join(root_dir, 'src'))
sys.path.insert(1,os.path.join(root_dir, 'env/lib/python3.5/site-packages'))