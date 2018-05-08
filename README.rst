stargaze
===========

version number: 0.0.1

|Build|
|Say thanks!|

Overview
--------

Looks up for words in a stardict dictionary.

Installation / Usage
--------------------

To install use pip:

::

    $ pip install stargaze

Or clone the repo:

::

    $ git clone https://github.com/codito/stargaze.git
    $ python setup.py install

Example
-------
.. code-block:: python

    >>> import stargaze                               
    >>> d = stargaze.Dictionary("./docs/words")            
    >>> d.lookup("word1")
    'word1_defn'
    >>> # let's lookup for a synonym
    ... d.lookup("word1_syn1")    
    'word1_defn'

License
-------
MIT

Contributing
------------

Pull requests are most welcome.

.. |Say thanks!| image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
   :target: https://saythanks.io/to/codito

.. |Build| image:: https://img.shields.io/travis/codito/stargaze.svg
    :target: https://travis-ci.org/codito/stargaze

