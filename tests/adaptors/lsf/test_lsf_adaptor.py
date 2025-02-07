#!/usr/bin/env python

__author__ = "Ioannis Paraskevakos"
__copyright__ = "Copyright 2018-2019, The SAGA Project"
__license__ = "MIT"


""" This test tests the LSF script generator function as well as the LSF adaptor
"""
import unittest

import radical.saga.url as surl
import radical.saga     as rs


# ------------------------------------------------------------------------------
#
class TestGenerator(unittest.TestCase):

    def setUp(self):
      # self._url = surl.Url('gsissh://summit.ccs.ornl.gov')
        self._url = surl.Url('gsissh://localhost')
        self._jd                 = rs.job.Description()
        self._jd.name            = 'Test'
        self._jd.executable      = '/bin/sleep'
        self._jd.arguments       = 60
        self._jd.environment     = {'test_env': 15}
        self._jd.output          = 'output.log'
        self._jd.error           = 'error.log'
        self._jd.queue           = 'normal-queue'
        self._jd.project         = 'TestProject'
        self._jd.wall_time_limit = 70
        self._jd.total_cpu_count = 65

        self._script = "\n#!/bin/bash \n" \
                     + "#BSUB -J Test \n" \
                     + "#BSUB -o output.log \n" \
                     + "#BSUB -e error.log \n" \
                     + "#BSUB -W 1:10 \n" \
                     + "#BSUB -q normal-queue \n" \
                     + "#BSUB -P TestProject \n" \
                     + "#BSUB -nnodes 2 \n" \
                     + "#BSUB -alloc_flags 'gpumps smt4' \n\n" \
                     + "export  test_env=15 \n" \
                     + "/bin/sleep 60 "

    def test_lsfscript_generator(self):

        from radical.saga.adaptors.lsf.lsfjob import _lsfscript_generator

        script = _lsfscript_generator(url=self._url, logger=None, jd=self._jd,
                                      ppn=None, lsf_version=None, queue=None,
                                      span=None)

        self.assertTrue(script == self._script)


# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

    suite = unittest.TestLoader().loadTestsFromTestCase(TestGenerator)
    unittest.TextTestRunner(verbosity=2).run(suite)


# ------------------------------------------------------------------------------

