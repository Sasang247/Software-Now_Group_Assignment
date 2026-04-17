"""
Encryption-Decryption Program
----------------------------------------
Reads text from 'raw_text.txt', encrypts it,
writes to 'encrypted_text.txt', then decrypts it,
and verifies correctness.

Author: Student
"""

# =========================
# Utility Functions
# =========================

def shift_lowercase(char, shift1, shift2):
    """
    Encrypt a lowercase character based on rules.
    """
    if 'a' <= char <= 'm':
        shift = shift1 * shift2
        return chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
    elif 'n' <= char <= 'z':
        shift = shift1 + shift2
        return chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
    return char


def shift_uppercase(char, shift1, shift2):
    """
    Encrypt an uppercase character based on rules.
    """
    if 'A' <= char <= 'M':
        shift = shift1
        return chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
    elif 'N' <= char <= 'Z':
        shift = shift2 ** 2
        return chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
    return char


def encrypt_character(char, shift1, shift2):
    """
    Encrypt a single character.
    """
    if char.islower():
        return shift_lowercase(char, shift1, shift2)
    elif char.isupper():
        return shift_uppercase(char, shift1, shift2)
    else:
        return char


# =========================
# Decryption Functions
# =========================

def decrypt_lowercase(char, shift1, shift2):
    """
    Decrypt a lowercase character.
    """
    if 'a' <= char <= 'm':
        shift = shift1 * shift2
        return chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
    elif 'n' <= char <= 'z':
        shift = shift1 + shift2
        return chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
    return char


def decrypt_uppercase(char, shift1, shift2):
    """
    Decrypt an uppercase character.
    """
    if 'A' <= char <= 'M':
        shift = shift1
        return chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
    elif 'N' <= char <= 'Z':
        shift = shift2 ** 2
        return chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
    return char


def decrypt_character(char, shift1, shift2):
    """
    Decrypt a single character.
    """
    if char.islower():
        return decrypt_lowercase(char, shift1, shift2)
    elif char.isupper():
        return decrypt_uppercase(char, shift1, shift2)
    else:
        return char


# =========================
# Input Function
# =========================

def get_shift_input(prompt):
    """
    Safely gets an integer shift value from the user.
    Repeats until valid input is entered.
    """
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")


# =========================
# Core Functions
# =========================

def encrypt_file(input_file, output_file, shift1, shift2):
    """
    Reads input file, encrypts content, writes to output file.
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        text = infile.read()

    encrypted_text = ""
    for char in text:
        encrypted_text += encrypt_character(char, shift1, shift2)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(encrypted_text)

    print("Encryption completed.")


def decrypt_file(input_file, output_file, shift1, shift2):
    """
    Reads encrypted file, decrypts content, writes to output file.
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        text = infile.read()

    decrypted_text = ""
    for char in text:
        decrypted_text += decrypt_character(char, shift1, shift2)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(decrypted_text)

    print("Decryption completed.")


def verify_files(original_file, decrypted_file):
    """
    Compares original and decrypted files.
    """
    with open(original_file, 'r', encoding='utf-8') as f1:
        original = f1.read()

    with open(decrypted_file, 'r', encoding='utf-8') as f2:
        decrypted = f2.read()

    if original == decrypted:
        print("Verification successful: Decrypted text matches original.")
    else:
        print("Verification failed: Decrypted text does not match original.")


# =========================
# Main Program
# =========================

def main():
    """
    Main execution flow.
    """
    print("Encryption Program")
    print("------------------------------")

    # User input
    shift1 = get_shift_input("Enter shift1: ")
    shift2 = get_shift_input("Enter shift2: ")

    # File names
    input_file = "raw_text.txt"
    encrypted_file = "encrypted_text.txt"
    decrypted_file = "decrypted_text.txt"

    # Process flow
    encrypt_file(input_file, encrypted_file, shift1, shift2)
    decrypt_file(encrypted_file, decrypted_file, shift1, shift2)
    verify_files(input_file, decrypted_file)


# Run program
if __name__ == "__main__":
    main()