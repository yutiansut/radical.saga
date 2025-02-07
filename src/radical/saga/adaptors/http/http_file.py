
__author__    = "Andre Merzky, Ole Weidner"
__copyright__ = "Copyright 2012-2013, The SAGA Project"
__license__   = "MIT"


""" file adaptor implementation on top tof the HTTP protocol
"""

import os
import urllib

import radical.utils as ru

from ...exceptions           import *
from ...                     import url        as rsurl
from ...utils                import pty_shell  as rsups
from ...utils                import misc       as rsumisc
from ...                     import filesystem as api_fs
from ...filesystem.constants import *
from ..                      import base       as a_base
from ..cpi                   import filesystem as cpi_fs
from ..cpi                   import decorators as cpi_decs

SYNC_CALL  = cpi_decs.SYNC_CALL
ASYNC_CALL = cpi_decs.ASYNC_CALL


# --------------------------------------------------------------------
# the adaptor name
#
_ADAPTOR_NAME          = "radical.saga.adaptors.http_file"
_ADAPTOR_SCHEMAS       = ["http", "https"]
_ADAPTOR_OPTIONS       = []

# --------------------------------------------------------------------
# the adaptor capabilities & supported attributes
#
_ADAPTOR_CAPABILITIES  = {
    "metrics"          : [],
    "contexts"         : {"userpass" : "username/password pair for ssh"}
}

# --------------------------------------------------------------------
# the adaptor documentation
#
_ADAPTOR_DOC           = {
    "name"             : _ADAPTOR_NAME,
    "cfg_options"      : _ADAPTOR_OPTIONS, 
    "capabilities"     : _ADAPTOR_CAPABILITIES,
    "description"      : """The HTTP file adpator allows file transfer (copy) from remote resources to the local machine via the HTTP/HTTPS protocol, similar to cURL.""",
    "example"          : "examples/files/http_file_copy.py",
    "schemas"          : {"http"   :"use the http protocol to access a remote file", 
                          "https"  :"use the https protocol to access a remote file"}
}

# --------------------------------------------------------------------
# the adaptor info is used to register the adaptor with SAGA

_ADAPTOR_INFO = {
    "name": _ADAPTOR_NAME,
    "version": "v0.1",
    "schemas": _ADAPTOR_SCHEMAS,
    "cpis": [
        {
            "type": "radical.saga.namespace.Entry",
            "class": "HTTPFile"
        },
        {
            "type": "radical.saga.filesystem.File",
            "class": "HTTPFile"
        }
    ]
}


###############################################################################
# The adaptor class
class Adaptor (a_base.Base):
    """
    This is the actual adaptor class, which gets loaded by SAGA (i.e. by the
    SAGA engine), and which registers the CPI implementation classes which
    provide the adaptor's functionality.
    """

    # ----------------------------------------------------------------
    #
    def __init__(self):

        a_base.Base.__init__(self, _ADAPTOR_INFO, _ADAPTOR_OPTIONS)

    # ----------------------------------------------------------------
    #
    def sanity_check(self):
        pass


###############################################################################
#
class HTTPFile (cpi_fs.File):
    """ Implements radical.saga.adaptors.cpi.filesystem.File
    """
    # ----------------------------------------------------------------
    #
    def __init__(self, api, adaptor):

        self._cpi_base = super(HTTPFile, self)
        self._cpi_base.__init__(api, adaptor)

    # ----------------------------------------------------------------
    #
    def __del__(self):
        self.finalize(kill=True)

    # ----------------------------------------------------------------
    #
    @SYNC_CALL
    def init_instance(self, adaptor_state, url, flags, session):

        # FIXME: eval flags!

        self._logger.info("init_instance %s" % url)

        if 'from_open' in adaptor_state and adaptor_state['from_open']:
            self.url = rsurl.Url(url)  # deep copy
            self.flags = flags
            self.session = session
            self.valid = False  # will be set by initialize
            self.cwdurl = rsurl.Url(adaptor_state["cwd"])
            self.cwd = self.cwdurl.path

            if rsumisc.url_is_relative(self.url):
                self.url = rsumisc.url_make_absolute(self.cwd, self.url)

        else:
            if rsumisc.url_is_relative(url):
                raise BadParameter("cannot interprete relative URL in this context ('%s')" % url)

            self.url = url
            self.flags = flags
            self.session = session
            self.valid = False  # will be set by initialize
            self.cwd = rsumisc.url_get_dirname(url)

            self.cwdurl = rsurl.Url(url)  # deep copy
            self.cwdurl.path = self.cwd

        self.initialize()
        return self.get_api()

    # ----------------------------------------------------------------
    #
    def initialize(self):

        if self.flags & CREATE_PARENTS:
            raise BadParameter("File creation not supported via HTTP(S)")

        elif self.flags & CREATE:
            raise BadParameter("File creation not supported via HTTP(S)")

        elif self.flags & WRITE:
            raise BadParameter("File write not supported via HTTP(S)")

        elif self.flags & READ:
            pass

        self.valid = True

    # ----------------------------------------------------------------
    #
    def finalize(self, kill=False):
        # nothing to do here
        pass

    # ----------------------------------------------------------------
    #
    @SYNC_CALL
    def get_url(self):
        return rsurl.Url(self.url)  # deep copy

    # ----------------------------------------------------------------
    #
    @SYNC_CALL
    def copy_self(self, tgt_in, flags):

        src = rsurl.Url(self.url)  # deep copy
        tgt = rsurl.Url(tgt_in)  # deep copy

        if tgt.scheme != 'file':
            raise BadParameter("Only file://localhost URLs are supported as copy targets.")

        if tgt.host != 'localhost':
            raise BadParameter("Only file://localhost URLs are supported as copy targets.")

        #if rsumisc.url_is_relative (src) : src = rsumisc.url_make_absolute (cwdurl, src)
        #if rsumisc.url_is_relative (tgt) : tgt = rsumisc.url_make_absolute (cwdurl, tgt)

        target = ""

        src_filename = os.path.basename(src.path)
        local_path = tgt.path
        if os.path.exists(tgt.path):
            if os.path.isfile(tgt.path):
                # fail if overwtrite flag is not set, otherwise copy
                if flags & OVERWRITE:
                    target = local_path
                else:
                    raise BadParameter("Local file '%s' exists." % local_path)

            elif os.path.isdir(tgt.path):
                # add source filename to target path
                target = os.path.join(local_path, src_filename)

                if os.path.exists(target):
                    if not flags & OVERWRITE:
                        raise BadParameter("Local file '%s' exists." % target)

        try:
            urllib.urlretrieve(str(src), target)
        except Exception, e:
            raise BadParameter("Couldn't copy %s to %s: %s" %
                                    (str(src), target, str(e)))

    # ----------------------------------------------------------------
    #
    @SYNC_CALL
    def is_dir_self(self):
        return False

    # ----------------------------------------------------------------
    #
    @SYNC_CALL
    def is_entry_self(self):
        return True

    # ----------------------------------------------------------------
    #
    @SYNC_CALL
    def is_link_self(self):
        return False

    # ----------------------------------------------------------------
    #
    @SYNC_CALL
    def is_file_self(self):
        return True
