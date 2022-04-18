#!/usr/bin/python
#import Crypto

from Crypto.Cipher import AES
import scrypt
import hashlib
from bitcoin import *
import binascii
import base58

def bip38_encrypt(privkey,passphrase):
    '''BIP0038 non-ec-multiply encryption. Returns BIP0038 encrypted privkey.'''
    privformat = get_privkey_format(privkey)
    if privformat in ['wif_compressed','hex_compressed']:
        compressed = True
        flagbyte = b'\xe0'
        if privformat == 'wif_compressed':
            privkey = encode_privkey(privkey,'hex_compressed')
            privformat = get_privkey_format(privkey)
    if privformat in ['wif', 'hex']:
        compressed = False
        flagbyte = b'\xc0'
    if privformat == 'wif':
        privkey = encode_privkey(privkey,'hex')
        privformat = get_privkey_format(privkey)
    
    pubkey = privtopub(privkey)
    addr = pubtoaddr(pubkey)

    #print ("hashlib")
    #print (hashlib.sha256(hashlib.sha256(addr.encode('utf-8')).digest()).hexdigest())


    addresshash = hashlib.sha256(hashlib.sha256(addr.encode('utf-8')).digest()).digest()[0:4]

    #addresshash2 = hashlib.sha256(hashlib.sha256(addr.encode('utf-8')).digest()).hexdigest()
    #addresshash2 = addresshash2[0:8]
    #print("addresshash2")
    #print(addresshash2[0:8])


    key = scrypt.hash(passphrase, addresshash, 16384, 8, 8)

    #hashed_key = binascii.hexlify(key)
    #print (hashed_key)

    derivedhalf1 = key[0:32]
    derivedhalf2 = key[32:64]


    aes = AES.new(derivedhalf2, AES.MODE_EAX) # `MODE_ECB` is insecure; this is preferable.
    encryptedhalf1 = aes.encrypt(binascii.unhexlify('%0.32x' % (int(privkey[0:32], 16) ^ int(binascii.hexlify(derivedhalf1[0:16]), 16))))
     
    encryptedhalf2 = aes.encrypt(binascii.unhexlify('%0.32x' % (int(privkey[32:64], 16) ^ int(binascii.hexlify(derivedhalf1[16:32]), 16))))
    encrypted_privkey = (b'\x01\x42' + flagbyte + addresshash + encryptedhalf1 + encryptedhalf2)
    encrypted_privkey += hashlib.sha256(hashlib.sha256(encrypted_privkey).digest()).digest()[:4] # b58check for encrypted privkey
    encrypted_privkey = base58.b58encode(encrypted_privkey)
    return encrypted_privkey


def bip38_decrypt(encrypted_privkey,passphrase):
    '''BIP0038 non-ec-multiply decryption. Returns WIF privkey.'''
    
    # Documentation from https://en.bitcoin.it/wiki/BIP_0038

    # 1. Collect encrypted private key and passphrase from user.
    d = base58.b58decode(encrypted_privkey.encode('utf_8'))
    d = d[2:]
    flagbyte = d[0:1]
    d = d[1:]
    if flagbyte == b'\xc0':
        compressed = False
    if flagbyte == b'\xe0':
        compressed = True

    addresshash = d[0:4]


    #print ("addresshash: " + str(addresshash))
    d = d[4:-4]

    # 3. Derive decryption key for seedb using scrypt with passpoint, addresshash, and ownerentropy
    key = scrypt.hash(passphrase,addresshash, 16384, 8, 8)
    derivedhalf1 = key[0:32]
    derivedhalf2 = key[32:64]

    encryptedhalf1 = d[0:16]
    encryptedhalf2 = d[16:32]
    aes = AES.new(derivedhalf2, AES.MODE_EAX)
    
    # 4. Decrypt encryptedpart2 using AES256Decrypt to yield the last 8 bytes of seedb and the last 8 bytes of encryptedpart1.
    decryptedhalf2 = aes.decrypt(encryptedhalf2)
    # 5. Decrypt encryptedpart1 to yield the remainder of seedb.
    decryptedhalf1 = aes.decrypt(encryptedhalf1)


    priv = decryptedhalf1 + decryptedhalf2

    # 7. Multiply passfactor by factorb mod N to yield the private key associated with generatedaddress.
    priv = binascii.unhexlify('%064x' % (int(binascii.hexlify(priv), 16) ^ int(binascii.hexlify(derivedhalf1), 16)))
    pub = privtopub(priv)
    if compressed:
        pub = encode_pubkey(pub,'hex_compressed')
        wif = encode_privkey(priv,'wif_compressed')
    else:
        wif = encode_privkey(priv,'wif')

    # 8. Convert that private key into a Bitcoin address, honoring the compression preference specified in the encrypted key.
    addr = pubtoaddr(pub)


    # 9. Hash the Bitcoin address, and verify that addresshash from the encrypted private key record matches the hash. If not, report that the passphrase entry was incorrect.
    if hashlib.sha256(hashlib.sha256(addr.encode('utf-8')).digest()).digest()[0:4] != addresshash:
        print('Verification failed. Password is incorrect.')
        #print(hashlib.sha256(hashlib.sha256(addr.encode('utf-8')).digest()).digest()[0:4])
        #print(addresshash)
        return ''
    else:
        return wif

