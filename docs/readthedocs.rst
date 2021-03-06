.. Asterisk IVR documentation master file, created by
   sphinx-quickstart on Mon Nov 14 16:14:39 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

****   
Read the Docs
****

The real **power** of Read the Docs is the ability to generate documentation from the docstrings contained within your code.  *The only problem is how to generate this documentation, isn't documented well.*

Banging on the Keyboard
=========

Getting it working, getting Read the Docs to generate documentation using the docstrings was a frustrating experience.  Lot's of *Banging on the Keyboard*, trying different things, and making changes all over the place.

Installing ``sphinx`` locally and running ``sphinx-quickstart`` **may** have been the solution.  

*..or helped get closer to making the documentation with* ``docstrings.``

Importing Python Docstrings
=========

Dealing with external modules or system I/O, `Read the Docs <https://readthedocs.org/>`_ is **not** importing the docstrings.  It's not showing any output from the module.  See: Basic Settings which *should* import the docstrings shown below::

	# -*- coding: utf-8 -*-
	"""
	A Simple Example
	"""
	
	from asterisk.agi import *

	myVar = 'some data'
	"""
	A Simple Variable
	"""

	agi = AGI()
	"""
	Create an AGI Instance 
	"""
	
	agi.answer()
	"""
	I/O Communications: stdin, stdout, and stderr
	"""

.. warning:: 

	This does not work.  `Read the Docs <https://readthedocs.org/>`_  doesn't display anything.
	
	It appears to choke when it reaches ``agi = AGI()`` unless **Install Project** is 
	enabled in  `Read the Docs <https://readthedocs.org/>`_.
	
	This happens because ``AGI()`` calls an external module.
	


.. warning:: 

	``agi.answer()`` does not work, with or without `Read the Docs <https://readthedocs.org/>`_  installing the project inside a virtualenv.
	
	It appears to choke when it reaches ``agi.answer()``
	
	The is probably due to the ``answer()`` function working with ``stdin`` and ``stdout``.

Mock
---------

It appears there **may** be a way to ``mock`` the module function.  Telling `Read the Docs <https://readthedocs.org/>`_ that it **should not** test the function.  But I have not been able to do this successfully. 


.. toctree::
   :maxdepth: 2
   :glob: