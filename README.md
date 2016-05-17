HyperTrack Python Bindings
==========================
[![Build Status](https://travis-ci.org/hypertrack/hypertrack-python.svg)](https://travis-ci.org/hypertrack/hypertrack-python/)
[![PyPI version](https://badge.fury.io/py/hypertrack.svg)](https://badge.fury.io/py/hypertrack)
[![Coverage Status](https://coveralls.io/repos/github/hypertrack/hypertrack-python/badge.svg?branch=master)](https://coveralls.io/github/hypertrack/hypertrack-python?branch=master)
[![Code Health](https://landscape.io/github/hypertrack/hypertrack-python/master/landscape.png)](https://landscape.io/github/hypertrack/hypertrack-python/master)
[![Slack Status](http://slack.hypertrack.io/badge.svg)](http://slack.hypertrack.io)

A python wrapper for the [HyperTrack api](http://docs.hypertrack.io).

Installation
------------
```
pip install hypertrack
```

Usage
------

You'll need your hypertrack secret key. You can find this from your account page.
Then, you can just import hypertrack and set your secret key on it.

```python
import hypertrack

hypertrack.secret_key = 'c237rtyfeo9893u2t4ghoevslsd'

customer = hypertrack.Customer.create(
    name='John Doe',
    email='john@customer.com',
    phone='+15555555555',
)

print customer
```

Documentation
-------------

For detailed documentation of the methods available, please visit the official [HyperTrack API documentation](http://docs.hypertrack.io).

Testing
-------
We commit to being compatible with Python 2.6+, Python 3.3+ and PyPy. We need to test against all of these environments to ensure compatibility. Travis CI will automatically run our tests on push. For local testing, we use pytest to handle testing across environments.

You will need to install pytest first which you can do using the following command:
```
pip install pytest
```

For running the tests, use the following command:
```
py.test
```
This will run all the tests for the packages.
