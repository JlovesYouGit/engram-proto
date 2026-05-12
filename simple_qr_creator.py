#!/usr/bin/env python3
"""
Simple QR Creator
Creates a working QR code using a more direct approach.
"""

import qrcode
import base64
import os
from PIL import Image, ImageDraw
import hashlib

def create_working_qr():
    """Create a working QR code with simpler approach."""
    
    print("🎯 Creating Working QR Code")
    print("=" * 30)
    
    # Read merged data
    data_file = "merged_vectors.data"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return
    
    with open(data_file, 'rb') as f:
        merged_data = f.read()
    
    print(f"✓ Read data: {len(merged_data)} bytes")
    
    # Create a simpler data representation
    # Instead of full binary, create a hash-based identifier
    data_hash = hashlib.sha256(merged_data).hexdigest()
    
    # Create a data packet with hash and size info
    data_packet = {
        "hash": data_hash,
        "size": len(merged_data),
        "type": "merged_vectors",
        "files": ["qr_vector_compressed.bin", "qr_pattern.bin"]
    }
    
    # Convert to JSON string
    import json
    json_data = json.dumps(data_packet, separators=(',', ':'))
    
    print(f"✓ JSON packet: {len(json_data)} characters")
    
    # Create QR code with JSON data
    try:
        qr = qrcode.QRCode(
            version=1,  # Auto-detect
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        
        qr.add_data(json_data)
        qr.make(fit=True)
        
        # Create image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Add visual enhancements
        draw = ImageDraw.Draw(qr_img)
        width, height = qr_img.size
        
        # Add purple corners (merged data indicator)
        corner_size = 40
        draw.rectangle([0, 0, corner_size, corner_size], fill="purple")
        draw.rectangle([width-corner_size, 0, width, corner_size], fill="purple")
        draw.rectangle([0, height-corner_size, corner_size, height], fill="purple")
        
        # Add center info
        center_x, center_y = width // 2, height // 2
        
        # Add text
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
            
            # Add "MERGED" text
            draw.text((center_x - 30, center_y - 60), "MERGED", fill="purple", font=font)
            draw.text((center_x - 20, center_y - 45), f"{len(merged_data)}B", fill="black", font=font)
            draw.text((center_x - 40, center_y - 30), data_hash[:8], fill="gray", font=font)
            
        except:
            pass
        
        # Save QR code
        output_file = "working_merged_qr.png"
        qr_img.save(output_file, quality=95)
        
        print(f"✅ Working QR saved: {output_file}")
        print(f"   Dimensions: {width}x{height}")
        print(f"   Data type: JSON packet")
        
        # Create reconstruction guide
        create_reconstruction_guide(output_file, data_packet, merged_data)
        
        return output_file
        
    except Exception as e:
        print(f"❌ QR creation failed: {e}")
        return None

def create_reconstruction_guide(qr_file: str, data_packet: dict, original_data: bytes):
    """Create reconstruction guide."""
    
    guide_file = qr_file.replace('.png', '_guide.txt')
    
    with open(guide_file, 'w') as f:
        f.write("Working QR Reconstruction Guide\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"QR File: {qr_file}\n\n")
        
        f.write("What this QR contains:\n")
        f.write(f"- Data hash: {data_packet['hash']}\n")
        f.write(f"- Data size: {data_packet['size']} bytes\n")
        f.write(f"- Data type: {data_packet['type']}\n")
        f.write(f"- Source files: {', '.join(data_packet['files'])}\n\n")
        
        f.write("How to get the full data:\n")
        f.write("1. Scan the QR code to get the JSON packet\n")
        f.write("2. Extract the hash from the JSON\n")
        f.write("3. Use the hash to verify the original data\n")
        f.write("4. The original data is in 'merged_vectors.data'\n")
        f.write("5. Verify the hash matches the original file\n\n")
        
        f.write("Verification Python Code:\n")
        f.write("import hashlib\n")
        f.write("import json\n\n")
        f.write("# Scan QR and get JSON\n")
        f.write("scanned_json = '...'  # Your scanned data\n")
        f.write("data = json.loads(scanned_json)\n")
        f.write("expected_hash = data['hash']\n\n")
        f.write("# Verify original data\n")
        f.write("with open('merged_vectors.data', 'rb') as f:\n")
        f.write("    original_data = f.read()\n\n")
        f.write("actual_hash = hashlib.sha256(original_data).hexdigest()\n")
        f.write("print(f'Hash matches: {actual_hash == expected_hash}')\n\n")
        
        f.write("Data Components:\n")
        f.write(f"- qr_vector_compressed.bin: {os.path.getsize('qr_vector_compressed.bin')} bytes\n")
        f.write(f"- qr_pattern.bin: {os.path.getsize('qr_pattern.bin')} bytes\n")
        f.write(f"- Total merged: {len(original_data)} bytes\n")
    
    print(f"📄 Guide saved: {guide_file}")

def create_data_access_tool():
    """Create a simple tool to access the merged data."""
    
    tool_code = '''#!/usr/bin/env python3
"""
Data Access Tool for Merged Vectors
"""

import hashlib
import json
import os

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
    print("\\nTo verify with scanned QR:")
    print("1. Scan the working_merged_qr.png")
    print("2. Copy the JSON data")
    print("3. Run: python data_access.py verify '<json_data>'")
    
    # Show file components
    print("\\n📁 File Components:")
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
            print("\\n✅ Verification successful! Data is authentic.")
        else:
            print("\\n❌ Verification failed! Data may be corrupted.")
            
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
'''
    
    with open("data_access.py", "w") as f:
        f.write(tool_code)
    
    print("📄 Data access tool created: data_access.py")

def main():
    """Main function."""
    
    # Create working QR
    qr_file = create_working_qr()
    
    if qr_file:
        # Create data access tool
        create_data_access_tool()
        
        print(f"\n🎯 Working QR System Complete!")
        print(f"   QR file: {qr_file}")
        print(f"   Data file: merged_vectors.data")
        print(f"   Access tool: data_access.py")
        print(f"   Guide: {qr_file.replace('.png', '_guide.txt')}")
        
        print(f"\n📱 How to use:")
        print(f"1. Scan {qr_file}")
        print(f"2. Get JSON packet with hash")
        print(f"3. Run: python data_access.py verify '<json>'")
        print(f"4. Verify data authenticity")
        print(f"5. Access merged vector data")
    else:
        print("❌ QR creation failed!")

if __name__ == "__main__":
    main()
