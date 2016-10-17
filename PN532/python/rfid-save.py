# Requires Adafruit_Python_PN532

import binascii
import sys
import struct

import Adafruit_PN532 as PN532

# Hack to make code compatible with both Python 2 and 3 (since 3 moved
# raw_input from a builtin to a different function, ugh).
try:
    input = raw_input
except NameError:
    pass

# PN532 configuration for a Raspberry Pi GPIO:

# GPIO 18, pin 12
CS   = 18
# GPIO 23, pin 16
MOSI = 23
# GPIO 24, pin 18
MISO = 24
# GPIO 25, pin 22
SCLK = 25

# Configure the key to use for writing to the MiFare card.  You probably don't
# need to change this from the default below unless you know your card has a
# different key associated with it.
CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]


# Create and initialize an instance of the PN532 class.
pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
pn532.begin()
pn532.SAM_configuration()

# Step 1, wait for card to be present.
print('PN532 NFC Module Writer')
print('')
print('== STEP 1 =========================')
print('Place the card to be written on the PN532...')
uid = pn532.read_passive_target()
while uid is None:
    uid = pn532.read_passive_target()
print('')
print('Found card with UID: 0x{0}'.format(binascii.hexlify(uid)))
print('')
print('==============================================================')
print('WARNING: DO NOT REMOVE CARD FROM PN532 UNTIL FINISHED WRITING!')
print('==============================================================')
print('')

# Step 2, pick a block type.
print('== STEP 2 =========================')
block_choice = None
while block_choice is None:
    print('')
    block_choice = input('Enter user ID: ')
    try:
        block_choice = int(block_choice)
    except ValueError:
        print('Error! Unrecognized option.')
        continue
    # Unsigned int in 4 bytes (32 bits)
    if not (0 <= block_choice < 4294967295):
        print('Error! User ID must be within 0 to 4294967295.')
        continue
    print('')
print('You chose the block type: {0}'.format(block_choice))
print('')

# Confirm writing the block type.
print('== STEP 3 =========================')
print('Confirm you are ready to write to the card:')
print('User ID: {0}'.format(block_choice))
choice = input('Confirm card write (Y or N)? ')
if choice.lower() != 'y' and choice.lower() != 'yes':
    print('Aborted!')
    sys.exit(0)
print('Writing card (DO NOT REMOVE CARD FROM PN532)...')

# Write the card!
# First authenticate block 4.
if not pn532.mifare_classic_authenticate_block(uid, 4, PN532.MIFARE_CMD_AUTH_B,
                                               CARD_KEY):
    print('Error! Failed to authenticate block 4 with the card.')
    sys.exit(-1)
# Next build the data to write to the card.
# Format is as follows:
# - Bytes 0-4 are a header with ASCII value 'TEST'
# - Bytes 4-7 is the user data, for example an unsigned int with user ID
data = bytearray(16)
# Add header 'TEST'
data[0:4] = b'TEST'
# Convert int to 4 bytes hex (with prefix 0 if shorter)
value = str(block_choice)
while (4 > len(value)):
    value = '0' + value
data[4:8] = value
# Finally write the card.
if not pn532.mifare_classic_write_block(4, data):
    print('Error! Failed to write to the card.')
    sys.exit(-1)
print('Wrote card successfully! You may now remove the card from the PN532.')