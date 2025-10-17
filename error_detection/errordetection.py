# -------------------------------------------------------
# Project: Bit Error Simulation using Python
# Topic: Error Detection and Correction Techniques
# Techniques: Parity Bit, Checksum, CRC-16
# -------------------------------------------------------

import random
import binascii

# -------------------------------
# Function to introduce bit errors
# -------------------------------
def introduce_error(binary_data):
#"""Randomly flips one bit in the binary data string"""#
    data = list(binary_data)
    pos = random.randint(0, len(data) - 1) # random bit position
    data[pos] = '1' if data[pos] == '0' else '0' # flip the bit
    return ''.join(data)

# -------------------------------
# Parity Bit Calculation
# -------------------------------
def parity_bit(data):
#"""Returns 1 if number of 1s is odd, else 0 (Even Parity)"""#
    count = data.count('1')
    return '0' if count % 2 == 0 else '1'

# -------------------------------
# Checksum Calculation
# -------------------------------
def checksum(data):
#"""Calculates simple checksum using ASCII values"""#
    total = sum(ord(ch) for ch in data)
    return total % 256 # 8-bit checksum

# -------------------------------
# CRC-16 Calculation
# -------------------------------
def crc16(data):
#"""Computes 16-bit CRC using binascii library"""#
    crc = binascii.crc_hqx(data.encode(), 0xFFFF)
    return format(crc, '04x') # return as hexadecimal string

# -------------------------------
# Helper: Convert ASCII to Binary
# -------------------------------
def to_binary(data):
#"""Converts ASCII text to binary string"""#
    return ''.join(format(ord(ch), '08b') for ch in data)

# -------------------------------
# MAIN PROGRAM
# -------------------------------
def main():
    print("=== Bit Error Simulation using Python ===\n")

# Step 1: Input data message
data = input("Enter a message to transmit: ").upper()
binary_data = to_binary(data)
print(f"\nOriginal Data (ASCII): {data}")
print(f"Binary Data: {binary_data}")

# Step 2: Calculate Parity, Checksum, and CRC
parity = parity_bit(binary_data)
cs = checksum(data)
crc = crc16(data)

print("\n--- Sender Side ---")
print(f"Parity Bit: {parity}")
print(f"Checksum: {cs}")
print(f"CRC-16: {crc}")

# Step 3: Introduce random bit error
error_data = introduce_error(binary_data)
print("\n--- Transmission ---")
print(f"Erroneous Binary Data: {error_data}")

# Step 4: Receiver recomputes values
recv_parity = parity_bit(error_data)
recv_cs = checksum(data) # Normally recomputed on received data
recv_crc = crc16(data) # Here using same message for demo

print("\n--- Receiver Side ---")
print(f"Received Parity Bit: {recv_parity}")
print(f"Received Checksum: {recv_cs}")
print(f"Received CRC: {recv_crc}")

# Step 5: Compare results
print("\n--- Results ---")
if parity != recv_parity:
    print("❌ Parity: Error Detected!")
else:
    print("✅ Parity: No Error Detected.")

if cs != recv_cs:
    print("❌ Checksum: Error Detected!")
else:
    print("✅ Checksum: No Error Detected.")

if crc != recv_crc:
    print("❌ CRC: Error Detected!")
else:
    print("✅ CRC: No Error Detected.")

print("\nSimulation Complete. Thank you!")

# Run the program
if __name__ == "__main__":
    main()