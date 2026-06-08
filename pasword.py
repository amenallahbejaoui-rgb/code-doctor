import bcrypt
print(bcrypt.hashpw(b"SuperSecret123", bcrypt.gensalt()).decode())