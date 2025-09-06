#!/usr/bin/env python3

import bcrypt

# Generate a proper bcrypt hash for the password "password"
password = "password"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

print(f"Bcrypt hash for 'password': {hashed.decode('utf-8')}")

# Verify it works
if bcrypt.checkpw(password.encode('utf-8'), hashed):
    print("Hash verification successful!")
else:
    print("Hash verification failed!")