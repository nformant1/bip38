# :closed_lock_with_key: BIP38

This is a fork from [decentropy/bip38](https://github.com/decentropy/bip38) updated to **Python 3.10** and an additional support for other coins.

This implementation supports

* BTC (mainnet / testnet)
* LTC (mainnet / testnet)
* DOGE (mainnet / testnet)

## :zap: Requirements

Required packages: (apt-get install) python-dev libssl-dev libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev

Required modules: (pip install) pycrypto scrypt bitcoin base58 pillow qrcode cryptos

(Credit: <https://github.com/surg0r/bip38> and <https://github.com/decentropy/bip38>)

## :camera: Example output

![Example Output](img/bip38_cmd.exe.png)
First to inputs (currency and testnet) have defaults (first choice in upper case)

Other optional inputs are marked as "(optional)"

![Example Paper Wallet](img/example.jpg)
Don't send any money to that wallet!
