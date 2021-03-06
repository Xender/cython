# -*- coding: utf-8 -*-
# tag: ipython

"""Tests for the Cython magics extension."""

import os
import sys

try:
    from IPython.testing.globalipapp import get_ipython
    from IPython.utils import py3compat
except:
    __test__ = False

from Cython.TestUtils import CythonTest

ip = get_ipython()
code = py3compat.str_to_unicode("""def f(x):
    return 2*x
""")


if sys.platform == 'win32':
    # not using IPython's decorators here because they depend on "nose"
    try:
        from unittest import skip as skip_win32
    except ImportError:
        # poor dev's silent @unittest.skip()
        def skip_win32(f):
            return lambda self: None
else:
    def skip_win32(f):
        return f


class TestIPythonMagic(CythonTest):

    def setUp(self):
        CythonTest.setUp(self)
        ip.extension_manager.load_extension('cython')

    def test_cython_inline(self):
        ip.ex('a=10; b=20')
        result = ip.run_cell_magic('cython_inline', '', 'return a+b')
        self.assertEqual(result, 30)

    @skip_win32
    def test_cython_pyximport(self):
        module_name = '_test_cython_pyximport'
        ip.run_cell_magic('cython_pyximport', module_name, code)
        ip.ex('g = f(10)')
        self.assertEqual(ip.user_ns['g'], 20.0)
        ip.run_cell_magic('cython_pyximport', module_name, code)
        ip.ex('h = f(-10)')
        self.assertEqual(ip.user_ns['h'], -20.0)
        try:
            os.remove(module_name + '.pyx')
        except OSError:
            pass

    def test_cython(self):
        ip.run_cell_magic('cython', '', code)
        ip.ex('g = f(10)')
        self.assertEqual(ip.user_ns['g'], 20.0)

    def test_cython_name(self):
        # The Cython module named 'mymodule' defines the function f.
        ip.run_cell_magic('cython', '--name=mymodule', code)
        # This module can now be imported in the interactive namespace.
        ip.ex('import mymodule; g = mymodule.f(10)')
        self.assertEqual(ip.user_ns['g'], 20.0)

    @skip_win32
    def test_extlibs(self):
        code = py3compat.str_to_unicode("""
from libc.math cimport sin
x = sin(0.0)
        """)
        ip.user_ns['x'] = 1
        ip.run_cell_magic('cython', '-l m', code)
        self.assertEqual(ip.user_ns['x'], 0)
