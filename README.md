Fifa14Client
===========
Fifa14Client is a python library that allows you to interact with the Fifa 14 Ultimate Web App programmatically.

Features
=========
* Logging in
* Getting Coin Amount
* Searching
* Buying
* Listing for auction
* Quick Selling
* Getting Tradepile,Unassigned pile, and Watchlist
* Moving bewteen piles
* Removing from watchlist
* Removing from tradepile

Prerequisites
========
* [requests 2.x](http://www.python-requests.org/en/latest/)
* [Python 2.x](http://www.python.org/download/releases/2.7.6)

Example Usage
===========
You can find an example of usage in the main.py, but anyways:

```python
from Fifa14Client import LoginManager
from Fifa14Client import WebAppFunctioner
import ConfigParser
from extra import EAHash


def do_main():
    Config = ConfigParser.ConfigParser()
    Config.read("accounts_example.ini")
    for section in Config.sections():
        email = Config.get(section, 'Email')
        password = Config.get(section, 'Password')
        secret_answer = Config.get(section, 'Secret')
        security_hash = EAHash.EAHashingAlgorithm().EAHash(secret_answer)
        platform = Config.get(section, 'Platform')

        login = LoginManager.LoginManager(email,password,security_hash,platform)
        login.login()
        func = WebAppFunctioner.WebAppFunctioner(login)
        print func.credits



if __name__ == "__main__":
    do_main()
```

License
===========
The MIT License (MIT)

Copyright (c) 2013 T.J.Corley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
