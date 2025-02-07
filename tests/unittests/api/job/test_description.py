#!/usr/bin/env python

__author__    = "Andre Merzky, Ole Weidner"
__copyright__ = "Copyright 2012-2013, The SAGA Project"
__license__   = "MIT"


import radical.saga as rs


# ------------------------------------------------------------------------------
#
def test_deepcopy():
    """ Test deep copy """

    try:
        jd1 = rs.job.Description ()
        jd1.executable = '/bin/sleep'
        jd1.arguments  = ['1.3']
        jd2 = jd1.clone ()
        jd2.executable = '/bin/nanosleep'
        assert jd1.executable != jd2.executable, "%s != %s" % (jd1.executable, jd2.executable)
        assert jd1.arguments  == jd2.arguments 

    except rs.SagaException as se:
        assert False, "Unexpected exception: %s" % se

def test_environment_list ():
    """ Test environment support for list type """

    jd = rs.job.Description ()
    jd.environment = ['A=a', 'B=b']
    assert (type(jd.environment) == list), "Expected list() type but got %s" % type(jd.environment)
    assert (jd.environment == ['A=a', 'B=b']), "'%s' == '%s'" % (jd.environment, ['A=a', 'B=b'])
    
def test_environment_dict ():
    """ Test environment support for dict type """

    jd = rs.job.Description ()
    jd.environment = {'A':'a', 'B':'b'}
    assert (type(jd.environment) == dict), "Expected dict() type but got %s" % type(jd.environment)
    assert (jd.environment == {'A':'a', 'B':'b'}), "'%s' == '%s'" % (jd.environment, {'A':'a', 'B':'b'})
        
def test_environment ():
    """ Test environment type exceptions """

    try :
        jd = rs.job.Description ()
        jd.environment = 1
        assert (False), "expected BadParameter exception, got none"
    except rs.BadParameter :
        assert (True)
    except rs.SagaException as se:
        assert (False), "expected BadParameter exception, got %s" % se


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    test_deepcopy()
    test_environment_list()
    test_environment_dict()
    test_environment()


# ------------------------------------------------------------------------------

