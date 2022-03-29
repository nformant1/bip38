# bip38
fork from decentropy

## Test create
```
python.exe create-bip38.py
===============================================================
 BIP38 generator: Create paper wallet, encrypted with passphrase.
===============================================================  

Enter description for this wallet (optional):
Test Descr

Enter a WIF format private key (optional):

* generated new key *
wif: 5J3vJJgRvf2W9KarF5C6z5aPvi6HtmKmRRRKxb5ZXmEfkWhfV3h
addr :1CraM7jr6D7WWYtKCRNtDUvKpUjejz3RC9

Enter a secret passphrase:
Password:

Re-enter the passphrase:
Password:
flagbyte:       <class 'bytes'>
b'\xc0'
bip: b'6PRR9dL9bFAtyq9pMAkEwTDhr6juPBXZ22yVJWUQ2Z6DDMhqvdFHqTxGs2'

Enter passphrase hint (recommended):
pw: test
 
===============================================================
 Encrypted paper wallet (image file) created.

Bitcoin address:1CraM7jr6D7WWYtKCRNtDUvKpUjejz3RC9
Encrypted key:b'6PRR9dL9bFAtyq9pMAkEwTDhr6juPBXZ22yVJWUQ2Z6DDMhqvdFHqTxGs2'

 (To decrypt, run 'python unlock-bip38.py')
===============================================================
```

# Test unlock (fails)
```
python .\unlock-bip38.py
===============================================================
 BIP38 Unlock: decrypt a passphrase encrypted private key.
 (Always protect your private keys!)
===============================================================

Enter BIP38 encrypted key:
6PRR9dL9bFAtyq9pMAkEwTDhr6juPBXZ22yVJWUQ2Z6DDMhqvdFHqTxGs2

Enter secret passphrase:
test

Traceback (most recent call last):
  File "C:\Users\nformant\Documents\bip_38_python3\unlock-bip38.py", line 22, in <module>
    wif = bip38_decrypt(bip, pasw)
  File "C:\Users\nformant\Documents\bip_38_python3\bip38.py", line 56, in bip38_decrypt
    unencoded_string = str(bytearray.fromhex( encrypted_privkey ))
ValueError: non-hexadecimal number found in fromhex() arg at position 1
```
