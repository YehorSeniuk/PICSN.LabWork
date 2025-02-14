import random
import time
import hashlib
from tinyec import registry
from docx import Document

# Використовуємо невелике число для демонстраційного простору ключів (наприклад, 9973)
RESTRICTED_MAX = 9973

def generate_restricted_private_key(curve, max_val=RESTRICTED_MAX):
    """
    Генеруємо приватний ключ як випадкове число в діапазоні [1, max_val).
    """
    return random.randint(1, max_val - 1)

def brute_force_ecdsa(target_pub_point, curve, max_val=RESTRICTED_MAX):
    """
    Перебираємо можливі значення приватного ключа від 1 до max_val-1,
    вимірюємо час перебору та повертаємо значення, для якого обчислена публічна точка
    співпадає з цільовою.
    """
    target_x = target_pub_point.x
    target_y = target_pub_point.y
    start_time = time.time()
    
    for guess in range(1, max_val):
        pub_guess = guess * curve.g  # обчислення публічної точки для 'guess'
        if pub_guess.x == target_x and pub_guess.y == target_y:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"[Brute Force] Знайдено ключ після {guess} спроб: приватний ключ = {guess}")
            print(f"[Brute Force] Час перебору: {elapsed:.6f} секунд")
            return guess
    
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"[Brute Force] Приватний ключ не знайдено. Час перебору: {elapsed:.6f} секунд")
    return None

def sign_message(message, d, curve, order):
    """
    Генерує цифровий підпис за алгоритмом ECDSA (спрощена версія для демонстрації)
    з використанням приватного ключа d та порядку order (реальний порядок кривої).
    """
    # Обчислюємо хеш повідомлення та беремо його за модулем order
    e = int.from_bytes(hashlib.sha256(message).digest(), 'big') % order
    while True:
        k = random.randint(1, order - 1)
        R = k * curve.g
        r = R.x % order
        if r == 0:
            continue
        try:
            k_inv = pow(k, -1, order)
        except ValueError:
            continue
        s = (k_inv * (e + d * r)) % order
        if s == 0:
            continue
        return (r, s)

def verify_signature(message, signature, Q, curve, order):
    """
    Верифікує цифровий підпис (r, s) для повідомлення та публічного ключа Q.
    """
    r, s = signature
    if not (1 <= r < order and 1 <= s < order):
        return False
    e = int.from_bytes(hashlib.sha256(message).digest(), 'big') % order
    try:
        s_inv = pow(s, -1, order)
    except ValueError:
        return False
    u1 = (e * s_inv) % order
    u2 = (r * s_inv) % order
    point = u1 * curve.g + u2 * Q
    return (point.x % order) == r

if __name__ == '__main__':
    # Отримуємо криву secp256r1 з tinyec
    curve = registry.get_curve('secp256r1')
    
    # Спробуємо отримати порядок кривої через атрибут n
    order = getattr(curve, "n", None)
    if order is None:
        # Якщо атрибут n відсутній, для secp256r1 використовуємо захардкоджене значення
        if curve.name.lower() == "secp256r1":
            order = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
        else:
            raise ValueError("Порядок кривої для {} не визначено.".format(curve.name))
    
    # Генеруємо демонстраційну пару ключів із обмеженого простору (для брутфорсу)
    d = generate_restricted_private_key(curve)
    Q = d * curve.g
    print("Згенерований обмежений приватний ключ (d):", d)
    print("Публічний ключ (Q):", (Q.x, Q.y))
    
    # Брутфорс: намагаємось відновити приватний ключ по публічній точці Q
    recovered_d = brute_force_ecdsa(Q, curve, RESTRICTED_MAX)
    
    # Зчитування вхідного тексту з файлу input.docx за допомогою python-docx
    document = Document("input.docx")
    doc_text = "\n".join([para.text for para in document.paragraphs])[:1000]
    message = doc_text.encode('utf-8')
    print("\nЗчитаний текст з input.docx:")
    print(doc_text)
    
    # Накладання підпису з вимірюванням часу (використовуємо реальний порядок кривої)
    start_sign = time.time()
    signature = sign_message(message, d, curve, order)
    end_sign = time.time()
    sign_time = end_sign - start_sign
    print("\nНакладений підпис (r, s):", signature)
    print(f"Час накладання підпису: {sign_time:.6f} секунд")
    
    # Верифікація підпису з вимірюванням часу
    start_verify = time.time()
    valid = verify_signature(message, signature, Q, curve, order)
    end_verify = time.time()
    verify_time = end_verify - start_verify
    print("\nРезультат верифікації підпису:", valid)
    print(f"Час верифікації підпису: {verify_time:.6f} секунд")

