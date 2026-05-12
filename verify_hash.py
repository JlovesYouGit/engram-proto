#!/usr/bin/env python3
import hashlib

def calculate_sha256(data):
    """Calculate SHA256 hash of given data."""
    return hashlib.sha256(data).hexdigest()

# Read the file and verify hash
with open('qr_pattern.bin', 'rb') as f:
    # Read header until we find the binary data
    header_lines = []
    while True:
        line = f.readline()
        if line == b'' or line == b'\n':
            break
        header_lines.append(line.decode('utf-8').strip())
        if line.decode('utf-8').strip().startswith('DEPTH'):
            break
    
    # Read the binary data
    binary_data = f.read()
    
    print("Header lines:")
    for i, line in enumerate(header_lines):
        print(f"  {i}: {line}")
    
    print(f"\nBinary data size: {len(binary_data)} bytes")
    
    # Calculate hash
    file_hash = calculate_sha256(binary_data)
    print(f"File SHA256: {file_hash}")
    
    # Expected hash from header
    expected_hash = header_lines[4]  # SHA256 is at index 4
    print(f"Expected SHA256: {expected_hash}")
    
    print(f"Hash verification: {'✓ PASS' if file_hash == expected_hash else '✗ FAIL'}")
