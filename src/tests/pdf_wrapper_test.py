import unittest

#import runserver
import sys
import json
import os
sys.path.append('../../src')
from utils import pdf_wrapper

from runserver import app as application


class TestPDFWrapperFunctions(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_hello(self):
        print  application.config["APP_PATH"]
    
    def test_build(self):

        application.app_context().push()
        json_form=open(application.config["APP_PATH"] +'/src/etc/estructura.json')
        form = json.load(json_form)
        data = {}
        print pdf_wrapper.build(form, data)    

if __name__ == '__main__':
    unittest.main()