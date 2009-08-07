import os
import unittest

import dwl_multidop
from dwl_multidop_exceptions import *

project_path = os.path.join(os.path.dirname(__file__), '..')
class TestMain(unittest.TestCase):

    def testmain(self):
        self.assertRaises(IOError, dwl_multidop.main, 'a_nonexistent_file.tx3')
        self.assertRaises(ExtensionError, dwl_multidop.main, 'nla100.exe')
        self.assertEqual(dwl_multidop.main(os.path.join(project_path,
            'data_for_tests', 'tcd_test_2', 'NLA168.TX2')),
            None)


