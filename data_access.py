#!/usr/bin/env python3
"""
Data Access Tool for Merged Vectors
"""

import hashlib
import json
import os
import sys

def verify_merged_data():
    """Verify and access merged vector data."""
    
    print("🔍 Merged Vector Data Access Tool")
    print("=" * 40)
    
    # Check if data file exists
    data_file = "merged_vectors.data"
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    # Read and hash the data
    with open(data_file, 'rb') as f:
        merged_data = f.read()
    
    actual_hash = hashlib.sha256(merged_data).hexdigest()
    
    print(f"✓ Data file: {data_file}")
    print(f"✓ Size: {len(merged_data)} bytes")
    print(f"✓ Hash: {actual_hash}")
    
    # If user provides scanned hash, verify
    print("\nTo verify with scanned QR:")
    print("1. Scan the working_merged_qr.png")
    print("2. Copy the JSON data")
    print("3. Run: python data_access.py verify '<json_data>'")
    
    # Show file components
    print("\n📁 File Components:")
    if os.path.exists("qr_vector_compressed.bin"):
        size = os.path.getsize("qr_vector_compressed.bin")
        print(f"  ✓ qr_vector_compressed.bin: {size} bytes")
    
    if os.path.exists("qr_pattern.bin"):
        size = os.path.getsize("qr_pattern.bin")
        print(f"  ✓ qr_pattern.bin: {size} bytes")
    
    return actual_hash

def verify_scanned_hash(scanned_json):
    """Verify hash from scanned QR."""
    
    try:
        data = json.loads(scanned_json)
        expected_hash = data['hash']
        expected_size = data['size']
        
        # Read actual data
        with open("merged_vectors.data", 'rb') as f:
            actual_data = f.read()
        
        actual_hash = hashlib.sha256(actual_data).hexdigest()
        actual_size = len(actual_data)
        
        print("🔍 Verification Results:")
        print(f"  Hash match: {'✓' if actual_hash == expected_hash else '✗'}")
        print(f"  Size match: {'✓' if actual_size == expected_size else '✗'}")
        print(f"  Expected: {expected_hash[:16]}... ({expected_size} bytes)")
        print(f"  Actual: {actual_hash[:16]}... ({actual_size} bytes)")
        
        if actual_hash == expected_hash and actual_size == expected_size:
            print("\n✅ Verification successful! Data is authentic.")
        else:
            print("\n❌ Verification failed! Data may be corrupted.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        if len(sys.argv) > 2:
            verify_scanned_hash(sys.argv[2])
        else:
            print("Usage: python data_access.py verify '<json_data>'")
    else:
        verify_merged_data()
