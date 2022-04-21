import os
from bip38 import encrypt
from bitcoin import encode_privkey, random_key
from qrcode import QRCode, ERROR_CORRECT_Q, ERROR_CORRECT_M
from PIL import Image, ImageFont, ImageDraw
import getpass
from cryptos import Bitcoin, Litecoin, Doge


verbose = 1


print("===============================================================")
print(" BIP38 generator: Create paper wallet, encrypted with passphrase.")
print("===============================================================")

check = 0
while check == 0:
    print(" ")
    print("Enter crypto currency (BTC, LTC, DOGE) you want to choose (BTC/ltc/doge):")
    currency = input().upper()
    if currency in ["BTC", "LTC", "DOGE", ""]:
        check = 1
    else:
        print("The currency \"" + currency +
              "\" wasn't found. Please use BTC, LTC or DOGE")

if currency == "":
    currency = "BTC"

print(" ")
print("Do you want to use the testnet? (N/y):")
testnet = input().upper()

print(" ")
print("Enter description for this wallet (optional):")
name = input()
if currency == "":
    currency = "no"

# should be before that currency shit?
print(" ")
print("Enter a WIF format private key (optional):")
wif = input()

backgroundJPG = "assets/background.jpg"

if not wif:
    # randomkey = binascii.hexlify(os.urandom(32)).decode()
    if currency == "BTC" and testnet[:1] == "Y":
        c = Bitcoin(testnet=True)
        backgroundJPG = "assets/backgroundBTC.jpg"
    if currency == "BTC" and testnet[:1] != "Y":
        c = Bitcoin(testnet=False)
        backgroundJPG = "assets/backgroundBTC.jpg"
    if currency == "LTC" and testnet[:1] == "Y":
        c = Litecoin(testnet=True)
        backgroundJPG = "assets/backgroundLTC.jpg"
    if currency == "LTC" and testnet[:1] != "Y":
        c = Litecoin(testnet=False)
        backgroundJPG = "assets/backgroundLTC.jpg"
    if currency == "DOGE" and testnet[:1] == "Y":
        c = Doge(testnet=True)
    if currency == "DOGE" and testnet[:1] != "Y":
        c = Doge(testnet=False)

    wif = encode_privkey(random_key(), "wif")  # private key (WIF)

    print("* generated new key *")


# addr = privtoaddr(wif)
addr = c.privtoaddr(wif)

print(" ")
print("Enter a secret passphrase:")
pasw = getpass.getpass()
if not pasw:
    print("you must enter a passphrase")
    exit()

print(" ")
print("Re-enter the passphrase:")
pasw2 = getpass.getpass()
if pasw != pasw2:
    print("passphrase does not match")
    exit()

# encrypt
bip = encrypt(wif, pasw)
# if verbose: print ("bip: "+ str(bip))

print(" ")
print("Enter passphrase hint (recommended):")
hint = input()

# image...
img = Image.open(backgroundJPG)  # around 1000 x 500
# img = Image.new("RGB", (1000, 500), color = "red")

img_w, img_h = img.size

# QR image for addr
qr = QRCode(box_size=8, border=3, error_correction=ERROR_CORRECT_Q)
qr.add_data(addr)
im = qr.make_image()
im_w, im_h = im.size

# QR image for key
qr2 = QRCode(box_size=6, border=3, error_correction=ERROR_CORRECT_M)
qr2.add_data(bip)
im2 = qr2.make_image()
im2_w, im2_h = im2.size

# draw QRs
offs = (img_w - im_w - im2_w) / 4
img.paste(im, (int(offs*0.6), int((img_h-im_h)/2)))
img.paste(im2, (int(im_w+(3.5*offs)), int((img_h-im2_h)/2)))

# draw labels
draw = ImageDraw.Draw(img)
# font from https://www.dafont.com/de/monkey.font (marked as 100% free)
font = ImageFont.truetype(os.path.join("assets", "monkey.ttf"), 26)
fcolor = (0, 0, 0)

# print("fcolor: " + str(type(fcolor)))
# print("font: " + str(type(font)))


# draw.text((im_w+(3*offs),(img_h-im_h)/2-10), "BIP38 Key", fcolor, font)
draw.text((20, 20), name, fcolor, font)
draw.text((20, 70), "ADDRESS:  " + addr, fcolor, font)

# print("bip: " + str(type(bip)))
# print("fcolor: " + str(type(fcolor)))
# print("font: " + str(type(font)))

draw.text((20, (img_h - 100)), "BIP38 KEY:  " +
          bip.decode("utf-8"), fcolor, font)
if len(hint) > 0:
    draw.text((20, (img_h - 50)), "PASSPHRASE HINT:  " + hint, fcolor, font)


os.makedirs("out", exist_ok=True)
img.save(os.path.join("out", f"{currency}_{addr}.jpg"), "JPEG")

print(" ")
print("===============================================================")
print(" Encrypted paper wallet (image file) created.")
print(" ")

text = currency
if testnet[:1] == "Y":
    text = text + " (testnet)"

print(text + " address: " + addr)
print("Encrypted key: " + bip.decode("utf-8"))
if verbose:
    print("WIF: " + wif)
print(" ")
print(" (To decrypt, run \"python unlock-bip38.py\")")
print("===============================================================")
