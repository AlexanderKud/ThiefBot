# ThiefBot - 1000 BTC Puzzle Transaction Replacer

A python code which scans the BTC mempool for transaction from a specific wallet, and if found, then it takes public key from the transaction, and uses it to run Kangaroo.exe, which quickly finds the private key within a specified range using that Public Key. 
After getting the private key, it creates a raw transaction to a specified address
Signs the transaction using the private key
Then submits the transaction hex into the https://slipstream.mara.com/ Mining Pool for fast confirmation (hopefully) 

There are a few dependencies:
pip install time
pip install requests
pip install subprocess
pip install logging
pip install hashlib
pip install base58
pip install logging
pip install bitcoinlib
pip install selenium
pip install webdriver

You need to download chromedriver (make sure its the same version as your chrome browser version) 
ChromeDriver: https://googlechromelabs.github.io/chrome-for-testing/#stable

How to run:
(make sure u have python installed, and ran all the pip installs)
click on start.bat

If the code actually manages to replace the transaction, you'll know, cause you'll have 6.0 btc in your wallet

Editable Parameteres:
# Constants
API_KEY = 'apiKeyApiKeyApikey' # edit with your exchange.blockchain.com Api Key, find it in settings
WALLET_ADDRESS = '1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9'  # Update with target address, in this example its monitoring 67 address

f.write("200000000000000000\n")  # Specify start range hex
f.write("3fffffffffffffffff\n")  # Specify end range hex

recipient_address = 'bc1q77sekfapwfnvs9w5dwutcsjyf8lpf7sn0fmfgn' # your btc address where you wanna receive the prize coins

Also make sure you choose the correct path for your chromedriver:   service = Service('C:/Users/Computer/Desktop/chromedriver-win64/chromedriver.exe')
