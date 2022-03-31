from bip38 import *
from bitcoin import *


print ("===============================================================")
print (' BIP38 Unlock: decrypt a passphrase encrypted private key.')
print (" (Always protect your private keys!)")
print ("===============================================================")

print (" ")
print ('Enter BIP38 encrypted key:')
bip = input()

print (" ")
print ('Enter secret passphrase:')
pasw = input()
print (" ")

#decrypt
#bip = bytes(bip.encode('utf-8'))
#print (bip)
wif = bip38_decrypt(bip, pasw)

#print ("Address: " + privtoaddr(wif))
print ("Key: " + wif)
print (" ")
