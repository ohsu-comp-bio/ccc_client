#!/usr/bin/env python

#for debugging
import sys, os
import unittest

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
dir_path = os.path.dirname(dir_path)
sys.path.append(dir_path)

import ccc_client

# basic unit tests of the ccc_client services.  these should not depend on any of the services actually running.

class TestCccClient(unittest.TestCase):

    def test_index_names(self):
        token = self.generateAuthToken()
        ccc = ccc_client.ElasticSearchRunner(None, None, token)
        rp = ccc_client.ElasticSearchRunner.RowParser(None, self.getSiteId(), self.getUser(), self.getProject(), 'resource', None, ccc.DomainDescriptors, token, True)

        #index names
        self.assertEqual(rp.getIndexNameForDomain('resource'), self.getProject().lower() + '-' + 'aggregated-resource')
        self.assertEqual(rp.getIndexNameForDomain('sample'), self.getProject().lower() + '-' + 'sample')
        self.assertEqual(rp.getIndexNameForDomain('specimen'), self.getProject().lower() + '-' + 'specimen')
        self.assertEqual(rp.getIndexNameForDomain('patient'), self.getProject().lower() + '-' + 'patient')

        #row keys
        rowMap = {
            'patient_id': 'PATIENT1',
            'specimen_id': 'specImen1',
            'sample_id': 'saMple1',
            'ccc_did': 'ccc_did'
        }
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'resource'), 'ccc_did')
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'sample'), self.getProject().lower() + '-' + 'sample' + '-sample1')
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'specimen'), self.getProject().lower() + '-' + 'specimen-specimen1')
        self.assertEqual(rp.generateKeyForDomain(rowMap, 'patient'), self.getProject().lower() + '-' + 'patient-patient1')


    def test_import(self):
        token = self.generateAuthToken()
        ccc = ccc_client.ElasticSearchRunner(None, None, token, self.MockEs())

        #test not lack of errors
        fp = "mock/file.txt"
        rowMap = ccc.publish_resource(fp, self.getSiteId(), self.getUser(), self.getProject(), None, "application/text", "resource", None, {}, True)
        self.assertEqual(rowMap["filepath"], fp)
        self.assertEqual(rowMap["mimetype"], "application/text")

        #test mock inheritance
        rowMap = ccc.publish_resource('mock/file.txt', self.getSiteId(), self.getUser(), self.getProject(), None, "application/text", 'resource', 'abc', [], True)
        self.assertEqual(rowMap["inherit1"], "a")
        self.assertEqual(rowMap["inherit2"], "b")

        #test inheritance from other domain
        rowMap = ccc.publish_resource('mock/file.txt', self.getSiteId(), self.getUser(), self.getProject(), None, "application/text", 'resource', None, [
            "patient_id:patient1"
        ], True)
        self.assertFalse("inherit1" in rowMap.keys())
        self.assertFalse("inherit2" in rowMap.keys())
        self.assertEqual(rowMap["patientField1"], "a")
        self.assertEqual(rowMap["patientField2"], "b")


    class MockEs(object):
        def search(self, index=None, doc_type=None, ignore_unavailable=True, allow_no_indices=True,body=None):
            if "bool" in body["query"].keys():
                #this is called when searching for specific CCC_DID
                return {
                    "hits": {
                        "hits": [{
                            "_source": {
                                "inherit1": "a",
                                "inherit2": "b"
                            }
                        }]
                    }
                }
            elif "query_string" in body["query"].keys():
                #called when searching by patient_id
                return {
                    "hits": {
                        "hits": [{
                             "_source": {
                                 "patientField1": "a",
                                 "patientField2": "b"
                             }
                         }]
                    }
                }


    def index(self):
        print('indexing!')


    def generateAuthToken(self):
        #not yet implemented
        return 'notYetImplemented'

    def getScriptPath(self):
        return os.path.join(dir_path, './bin/ccc_import')

    def getSiteId(self):
        return 'testSite'

    def getProject(self):
        return 'testProject'

    def getUser(self):
        return 'me'

if __name__ == '__main__':
    unittest.main()
