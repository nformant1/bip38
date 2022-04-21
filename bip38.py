#!/usr/bin/python
from Cryptodome.Cipher import AES
import scrypt
import hashlib
from bitcoin import (
    get_privkey_format,
    encode_pubkey,
    encode_privkey,
    privkey_to_pubkey,
    pubkey_to_address
)
import binascii
import base58


def encrypt(privkey, passphrase):
    """BIP0038 non-ec-multiply encryption. Returns BIP0038 encrypted privkey."""
    privformat = get_privkey_format(privkey)
    if privformat in ["wif_compressed", "hex_compressed"]:
        flagbyte = b"\xe0"
        if privformat == "wif_compressed":
            privkey = encode_privkey(privkey, "hex_compressed")
            privformat = get_privkey_format(privkey)
    if privformat in ["wif", "hex"]:
        flagbyte = b"\xc0"
    if privformat == "wif":
        privkey = encode_privkey(privkey, "hex")
        privformat = get_privkey_format(privkey)

    pubkey = privkey_to_pubkey(privkey)
    addr = pubkey_to_address(pubkey)

    # print("hashlib")
    # print(hashlib.sha256(hashlib.sha256(addr.encode("utf-8")).digest()).hexdigest())

    addresshash = hashlib.sha256(hashlib.sha256(
        addr.encode("utf-8")).digest()).digest()[0:4]

    # addresshash2 = hashlib.sha256(hashlib.sha256(addr.encode("utf-8")).digest()).hexdigest()
    # addresshash2 = addresshash2[0:8]
    # print("addresshash2")
    # print(addresshash2[0:8])

    key = scrypt.hash(passphrase, addresshash, 16384, 8, 8)

    # hashed_key = binascii.hexlify(key)
    # print(hashed_key)

    derivedhalf1 = key[0:32]
    derivedhalf2 = key[32:64]

    # from python2 /Crypto/Cipher/AES.py Default is `MODE_ECB`.
    aes = AES.new(key=derivedhalf2, mode=AES.MODE_ECB)
    encryptedhalf1 = aes.encrypt(binascii.unhexlify("%0.32x" % (
        int(privkey[0:32], 16) ^ int(binascii.hexlify(derivedhalf1[0:16]), 16))))

    encryptedhalf2 = aes.encrypt(binascii.unhexlify("%0.32x" % (
        int(privkey[32:64], 16) ^ int(binascii.hexlify(derivedhalf1[16:32]), 16))))
    encrypted_privkey = (b"\x01\x42" + flagbyte +
                         addresshash + encryptedhalf1 + encryptedhalf2)
    # b58check for encrypted privkey
    encrypted_privkey += hashlib.sha256(
        hashlib.sha256(encrypted_privkey).digest()).digest()[:4]
    encrypted_privkey = base58.b58encode(encrypted_privkey)
    return encrypted_privkey


def decrypt(encrypted_privkey, passphrase):
    """BIP0038 non-ec-multiply decryption. Returns WIF privkey."""

    # Documentation from https://en.bitcoin.it/wiki/BIP_0038

    # 1. Collect encrypted private key and passphrase from user.
    decoded = base58.b58decode(encrypted_privkey.encode("utf_8"))
    decoded = decoded[2:]
    flagbyte = decoded[0:1]
    decoded = decoded[1:]
    if flagbyte == b"\xc0":
        compressed = False
    if flagbyte == b"\xe0":
        compressed = True

    addresshash = decoded[0:4]

    # print("addresshash: " + str(addresshash))
    decoded = decoded[4:-4]

    # 3. Derive decryption key for seedb using scrypt with passpoint, addresshash, and ownerentropy
    key = scrypt.hash(passphrase, addresshash, 16384, 8, 8)
    derivedhalf1 = key[0:32]
    derivedhalf2 = key[32:64]

    encryptedhalf1 = decoded[0:16]
    encryptedhalf2 = decoded[16:32]
    # from python2 /Crypto/Cipher/AES.py Default is `MODE_ECB`.
    aes = AES.new(key=derivedhalf2, mode=AES.MODE_ECB)

    # 4. Decrypt encryptedpart2 using AES256Decrypt to yield the last 8 bytes of seedb and the last 8 bytes of encryptedpart1.
    decryptedhalf2 = aes.decrypt(encryptedhalf2)
    # 5. Decrypt encryptedpart1 to yield the remainder of seedb.
    decryptedhalf1 = aes.decrypt(encryptedhalf1)

    priv = decryptedhalf1 + decryptedhalf2

    # 7. Multiply passfactor by factorb mod N to yield the private key associated with generatedaddress.
    priv = binascii.unhexlify("%064x" % (int(binascii.hexlify(
        priv), 16) ^ int(binascii.hexlify(derivedhalf1), 16)))
    pub = privkey_to_pubkey(priv)
    if compressed:
        pub = encode_pubkey(pub, "hex_compressed")
        wif = encode_privkey(priv, "wif_compressed")
    else:
        wif = encode_privkey(priv, "wif")

    # 8. Convert that private key into a Bitcoin address, honoring the compression preference specified in the encrypted key.
    addr = pubkey_to_address(pub)

    # 9. Hash the Bitcoin address, and verify that addresshash from the encrypted private key record matches the hash. If not, report that the passphrase entry was incorrect.
    if hashlib.sha256(hashlib.sha256(addr.encode("utf-8")).digest()).digest()[0:4] != addresshash:
        print("Verification failed. Password is incorrect.")
        # print(hashlib.sha256(hashlib.sha256(addr.encode("utf-8")).digest()).digest()[0:4])
        # print(addresshash)
        return ""
    else:
        return wif
