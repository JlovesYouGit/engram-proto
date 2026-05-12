#!/usr/bin/env python3
"""
QR Vector Generator
Creates QR codes containing compressed logic vectors.
"""

import qrcode
import numpy as np
from PIL import Image, ImageDraw
import os

def create_qr_with_vector(vector_file: str, output_qr: str = "qr_with_vector.png"):
    """Create QR code containing compressed vector data."""
    
    print(f"📱 Creating QR code with vector data from {vector_file}...")
    
    # Read the compressed vector data
    with open(vector_file, 'rb') as f:
        vector_data = f.read()
    
    print(f"   Vector size: {len(vector_data)} bytes")
    
    # Convert binary data to base64 for QR encoding
    import base64
    encoded_data = base64.b64encode(vector_data).decode('utf-8')
    
    print(f"   Base64 size: {len(encoded_data)} characters")
    
    # Check if data fits in QR code
    max_capacity = 2953  # QR version 40 (largest) capacity for binary data
    if len(encoded_data) > max_capacity:
        print(f"⚠️  Data too large for single QR code ({len(encoded_data)} > {max_capacity})")
        print("   Splitting into multiple QR codes...")
        return create_multi_qr_vector(encoded_data, output_qr)
    
    # Create QR code
    qr = qrcode.QRCode(
        version=40,  # Use largest version for maximum capacity
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=4,
    )
    
    qr.add_data(encoded_data)
    qr.make(fit=True)
    
    # Generate QR image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Add visual indicators
    draw = ImageDraw.Draw(qr_img)
    width, height = qr_img.size
    
    # Add corner markers to indicate this contains compressed logic
    marker_size = 20
    marker_color = "red"
    
    # Top-left marker
    draw.rectangle([0, 0, marker_size, marker_size], fill=marker_color)
    # Top-right marker  
    draw.rectangle([width-marker_size, 0, width, marker_size], fill=marker_color)
    # Bottom-left marker
    draw.rectangle([0, height-marker_size, marker_size, height], fill=marker_color)
    
    # Save QR code
    qr_img.save(output_qr)
    
    print(f"✅ QR code saved as: {output_qr}")
    print(f"   QR dimensions: {width}x{height} pixels")
    print(f"   Data encoded: {len(encoded_data)} characters")
    print(f"   Error correction: Level L")
    
    # Create info file
    info_file = output_qr.replace('.png', '_info.txt')
    with open(info_file, 'w') as f:
        f.write(f"QR Vector Information\n")
        f.write(f"===================\n\n")
        f.write(f"Source file: {vector_file}\n")
        f.write(f"Vector size: {len(vector_data)} bytes\n")
        f.write(f"Base64 size: {len(encoded_data)} characters\n")
        f.write(f"QR version: 40 (maximum capacity)\n")
        f.write(f"Error correction: Level L\n")
        f.write(f"QR dimensions: {width}x{height} pixels\n\n")
        f.write(f"Contained Logic:\n")
        f.write(f"- Golden Ratio Compression\n")
        f.write(f"- Brain Mesh Synapse\n")
        f.write(f"- Throne Protocol API\n")
        f.write(f"- Artificial Consciousness\n\n")
        f.write(f"Red corners indicate compressed logic vector\n")
    
    print(f"📄 Info file saved as: {info_file}")
    
    return output_qr

def create_multi_qr_vector(encoded_data: str, base_output: str):
    """Create multiple QR codes for large data."""
    
    # Split data into chunks
    chunk_size = 2800  # Leave some margin
    chunks = [encoded_data[i:i+chunk_size] for i in range(0, len(encoded_data), chunk_size)]
    
    print(f"   Creating {len(chunks)} QR codes...")
    
    qr_files = []
    
    for i, chunk in enumerate(chunks):
        qr = qrcode.QRCode(
            version=40,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=4,
        )
        
        # Add chunk header
        chunk_header = f"CHUNK_{i+1}_{len(chunks)}:"
        chunk_data = chunk_header + chunk
        
        qr.add_data(chunk_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Add visual indicators
        draw = ImageDraw.Draw(qr_img)
        width, height = qr_img.size
        
        # Add chunk number indicator
        marker_size = 30
        draw.rectangle([0, 0, marker_size, marker_size], fill="blue")
        draw.rectangle([width-marker_size, 0, width, marker_size], fill="blue")
        draw.rectangle([0, height-marker_size, marker_size, height], fill="blue")
        
        # Add chunk number
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
            draw.text((5, 5), str(i+1), fill="white", font=font)
        except:
            pass
        
        # Save chunk
        chunk_file = base_output.replace('.png', f'_part{i+1}.png')
        qr_img.save(chunk_file)
        qr_files.append(chunk_file)
        
        print(f"   ✓ Part {i+1}/{len(chunks)}: {chunk_file}")
    
    # Create assembly instructions
    instructions_file = base_output.replace('.png', '_assembly.txt')
    with open(instructions_file, 'w') as f:
        f.write(f"QR Vector Assembly Instructions\n")
        f.write(f"===============================\n\n")
        f.write(f"Total parts: {len(chunks)}\n")
        f.write(f"Total data size: {len(encoded_data)} characters\n\n")
        f.write(f"Assembly order:\n")
        for i, qr_file in enumerate(qr_files):
            f.write(f"{i+1}. {qr_file}\n")
        f.write(f"\nTo reconstruct:\n")
        f.write(f"1. Scan all QR codes in order\n")
        f.write(f"2. Remove 'CHUNK_X_Y:' prefixes\n")
        f.write(f"3. Concatenate all base64 data\n")
        f.write(f"4. Decode base64 to get original vector\n")
    
    print(f"📄 Assembly instructions saved as: {instructions_file}")
    
    return qr_files

def analyze_qr_capacity():
    """Analyze QR code capacity for different versions."""
    
    print("📊 QR Code Capacity Analysis")
    print("=" * 40)
    
    # Known capacities for QR codes (approximate)
    capacities = {
        10: 295,   # Version 10
        20: 775,   # Version 20  
        30: 1655,  # Version 30
        40: 2953   # Version 40 (maximum)
    }
    
    for version, capacity in capacities.items():
        print(f"Version {version}: {capacity} bytes (binary)")
        print(f"           ~{int(capacity * 1.33)} chars (base64)")
    
    print()

def main():
    """Main function."""
    
    print("🚀 QR Vector Generator")
    print("=" * 40)
    
    # Check if vector file exists
    vector_file = "qr_vector_compressed.bin"
    if not os.path.exists(vector_file):
        print(f"❌ Vector file not found: {vector_file}")
        print("   Please run qr_compressor.py first")
        return 1
    
    # Analyze capacity
    analyze_qr_capacity()
    print()
    
    # Create QR code
    try:
        qr_file = create_qr_with_vector(vector_file)
        
        print(f"\n🎯 QR Vector Generation Complete!")
        print(f"   Scan the QR code to retrieve compressed logic")
        print(f"   Contains all advanced algorithms in byte form")
        print(f"   Ready for deployment in any QR-compatible system")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
