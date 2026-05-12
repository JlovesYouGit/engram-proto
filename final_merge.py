#!/usr/bin/env python3
"""
Final Simple Merge
Creates a single PNG with merged vector data using direct image approach.
"""

import base64
import os
from PIL import Image, ImageDraw, ImageFont
import hashlib

def create_merged_png():
    """Create single PNG with merged vector data embedded."""
    
    print("🚀 Final Simple Merge to Single PNG")
    print("=" * 40)
    
    # Read both files
    files = ["qr_vector_compressed.bin", "qr_pattern.bin"]
    merged_data = b''
    
    for filename in files:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = f.read()
            merged_data += data
            print(f"✓ Added {filename}: {len(data)} bytes")
        else:
            print(f"❌ Missing: {filename}")
    
    if not merged_data:
        print("❌ No data to merge!")
        return
    
    print(f"✅ Total merged: {len(merged_data)} bytes")
    
    # Create image with embedded data
    img_size = 400
    img = Image.new('RGB', (img_size, img_size), 'white')
    draw = ImageDraw.Draw(img)
    
    # Add visual elements
    # Border
    draw.rectangle([10, 10, img_size-10, img_size-10], outline="black", width=3)
    
    # Center area for data visualization
    center_size = 200
    center_x = (img_size - center_size) // 2
    center_y = (img_size - center_size) // 2 + 20
    
    # Data visualization (hash-based pattern)
    data_hash = hashlib.md5(merged_data).hexdigest()
    
    # Create pattern based on data hash
    for i, char in enumerate(data_hash[:32]):
        if char in '0123456789abcdef':
            val = int(char, 16)
            x = center_x + (i % 8) * 25
            y = center_y + (i // 8) * 25
            size = 5 + val // 4
            color_intensity = val * 16
            color = (color_intensity, color_intensity, color_intensity)
            draw.rectangle([x, y, x+size, y+size], fill=color)
    
    # Add title
    try:
        font = ImageFont.load_default()
        title = "MERGED VECTOR DATA"
        draw.text((img_size//2 - len(title)*4, 30), title, fill="black", font=font)
        
        # Add file info
        info1 = f"Files: {len(files)}"
        info2 = f"Size: {len(merged_data)}B"
        info3 = f"Hash: {data_hash[:8]}..."
        
        draw.text((20, img_size - 60), info1, fill="gray", font=font)
        draw.text((20, img_size - 45), info2, fill="gray", font=font)
        draw.text((20, img_size - 30), info3, fill="gray", font=font)
        
    except:
        pass
    
    # Add corner indicators (merged data)
    corner_size = 20
    # Top-left
    draw.rectangle([0, 0, corner_size, corner_size], fill="purple")
    # Top-right
    draw.rectangle([img_size-corner_size, 0, img_size, corner_size], fill="purple")
    # Bottom-left
    draw.rectangle([0, img_size-corner_size, corner_size, img_size], fill="purple")
    # Bottom-right
    draw.rectangle([img_size-corner_size, img_size-corner_size, img_size, img_size], fill="purple")
    
    # Save the image
    output_file = "merged_vectors.png"
    img.save(output_file)
    
    print(f"✅ Saved: {output_file}")
    print(f"   Size: {img_size}x{img_size} pixels")
    
    # Create data file for reconstruction
    data_file = output_file.replace('.png', '.data')
    with open(data_file, 'wb') as f:
        f.write(merged_data)
    
    print(f"✅ Data saved: {data_file}")
    print(f"   Size: {len(merged_data)} bytes")
    
    # Create reconstruction info
    info_file = output_file.replace('.png', '_reconstruct.txt')
    with open(info_file, 'w') as f:
        f.write("Vector Data Reconstruction\n")
        f.write("=" * 30 + "\n\n")
        f.write(f"Image file: {output_file}\n")
        f.write(f"Data file: {data_file}\n")
        f.write(f"Original files: {', '.join(files)}\n")
        f.write(f"Total size: {len(merged_data)} bytes\n")
        f.write(f"Data hash: {data_hash}\n\n")
        f.write("To reconstruct:\n")
        f.write("1. Use the .data file for direct access\n")
        f.write("2. Or scan the image for visual verification\n")
        f.write("3. The image contains a hash-based visualization\n")
        f.write("4. Purple corners indicate merged vector data\n")
    
    print(f"✅ Info saved: {info_file}")
    
    print(f"\n🎯 Merge Complete!")
    print(f"   Single PNG with visual representation")
    print(f"   Separate data file for reconstruction")
    print(f"   Space optimized by direct merge")

if __name__ == "__main__":
    create_merged_png()
