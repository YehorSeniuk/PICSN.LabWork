import time

class VigenereCipher:
    def __init__(self, key):
        self.key = key

    def generate_key(self, text):
        """Розширення ключа до довжини тексту"""
        key = self.key
        while len(key) < len(text):
            key += key
        return key[:len(text)]

    def encrypt(self, plaintext):
        key = self.generate_key(plaintext)
        encrypted_text = ''
        for p, k in zip(plaintext, key):
            if p.isalpha():
                shift = ord(k.lower()) - ord('a')
                if p.islower():
                    encrypted_text += chr((ord(p) - ord('a') + shift) % 26 + ord('a'))
                else:
                    encrypted_text += chr((ord(p) - ord('A') + shift) % 26 + ord('A'))
            else:
                encrypted_text += p
        return encrypted_text

    def decrypt(self, ciphertext):
        key = self.generate_key(ciphertext)
        decrypted_text = ''
        for c, k in zip(ciphertext, key):
            if c.isalpha():
                shift = ord(k.lower()) - ord('a')
                if c.islower():
                    decrypted_text += chr((ord(c) - ord('a') - shift) % 26 + ord('a'))
                else:
                    decrypted_text += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            else:
                decrypted_text += c
        return decrypted_text

def brute_force_attack(ciphertext, wordlist):
    """Перебір можливих ключів з заданого словника"""
    decrypted_texts = []
    for key in wordlist:
        cipher = VigenereCipher(key)
        decrypted_text = cipher.decrypt(ciphertext)
        decrypted_texts.append((key, decrypted_text))
    return decrypted_texts

if __name__ == '__main__':
    key = "KEY"  # Ключ для шифру Віженера

    input_filename = 'plaintext.txt'
    output_filename = 'encrypted_text.txt'

    with open(input_filename, 'r', encoding='utf-8') as file:
        plaintext = file.read()

    print(f"Key: {key}")
    print('Input:', plaintext)
    print("--------------------------------------------------------------")

    cipher = VigenereCipher(key)

    start_time = time.time()
    encrypted_text = cipher.encrypt(plaintext)
    total_time = time.time() - start_time
    print('Encrypted text:', encrypted_text)
    print('Encryption time:', total_time, 'seconds')

    print("--------------------------------------------------------------")

    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(encrypted_text)

    start_time = time.time()
    decrypted_text = cipher.decrypt(encrypted_text)
    total_time = time.time() - start_time
    print('Decrypted text:', decrypted_text)
    print('Decryption time:', total_time, 'seconds')

    print("--------------------------------------------------------------")
    
    # Спроба зламу з використанням словника можливих ключів
    print('-------------- Brute Force Attack -----------------')
    wordlist = ["KEY", "SECRET", "PASSWORD"]  # Набір можливих ключів
    start_time = time.time()
    decrypted_texts = brute_force_attack(encrypted_text, wordlist)
    total_time = time.time() - start_time
    print('Total time for brute force attack:', total_time, 'seconds')

    print('Decrypted texts:')
    for key, text in decrypted_texts:
        if text == plaintext:
            print(f"Done, with key: {key}")
            print('Decrypted text:', text)
            break

