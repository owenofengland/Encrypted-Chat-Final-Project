import random
import math

def is_prime(num): #check if p1 and p2 are prime
    if num > 1:
        factors = 0
        for i in range(1, num):
            if num % i == 0:
                factors += 1
        if factors == 1:
            return True
    return False

def rand_abn(): #generates and returns product of two nonequal prime numbers (N)
    a = 0
    b = 0
    while not (is_prime(a) and is_prime(b) and a != b):
        a = random.randint(53, 1000)
        b = random.randint(53, 1000)
    n = a * b
    return n, a, b

def gen_phi(a, b): #finds phi of N, given prime one and prime two
    phi_a = a-1
    phi_b = b-1
    phi_n = phi_a * phi_b
    return phi_n

def find_factors(x):
    factors = set()
    for f in range(1, int(math.sqrt(x))+1):
        if x % f == 0:
            factors.add(f)
            factors.add(int(x/f))
    return factors

def gen_ekey(phi): #e has to be an odd number that is not a factor of phi
    factors = find_factors(phi)
    e = random.randint(3, 100)
    while e%2 == 0 or e in factors:
        e = random.randint(3, 100)
    return e

def gen_dkey(phi, e): #finds d given e and phi of N using modular inverse (e*d % mod(phi(n)) = 1)
    for d in range(3, phi):
        if d * e % phi == 1:
            return d

def gen_keys(): #generates keypairs, first is public keypair with e and n, second is private keypair with d and n
    d = None
    while d is None:
        n, a, b = rand_abn()
        phi = gen_phi(a, b)
        e = gen_ekey(phi)
        d = gen_dkey(phi, e)
    return (e, n), (d, n) #（public key), (private key)

def encrypt(pubkey, plaintext):
    e, n = pubkey
    ciphertext = [ord(char) ** e % n for char in plaintext]
    return ciphertext

def decrypt(privkey, ciphertext):
    d, n = privkey
    plaintext = ''
    for num in ciphertext:
        plaintext += chr(num**d % n)
    return plaintext
