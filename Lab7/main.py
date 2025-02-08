from sympy import mod_inverse, primefactors
import rsa
import time

def break_encryption(ciphertext, public_key):
    modulus = public_key.n
    exponent = public_key.e
    factors = primefactors(modulus)
    phi_value = (factors[0] - 1) * (factors[1] - 1)
    private_exponent = int(mod_inverse(exponent, phi_value))
    private_key = rsa.PrivateKey(modulus, exponent, private_exponent, factors[1], factors[0])
    decrypted_text = rsa.decrypt(ciphertext, private_key)

(public_key, private_key) = rsa.newkeys(128)

with open('message.txt', encoding='utf-8') as file:
    plaintext = file.read()

print("Input text =", plaintext)

# Шифрування
start_time = time.time()
encrypted_data = rsa.encrypt(plaintext.encode('utf-8'), public_key)
encryption_time = time.time() - start_time
print('Total encrypt time:', encryption_time)
print(encrypted_data)

# Розшифрування
start_time = time.time()
decrypted_data = rsa.decrypt(encrypted_data, private_key)
decryption_time = time.time() - start_time
print('Total decrypt time:', decryption_time)
print(decrypted_data.decode('utf-8'))

# Взлом (break_encryption)
start_time = time.time()
break_encryption(encrypted_data, public_key)
attack_time = time.time() - start_time
print('Total break_encryption time:', attack_time)

