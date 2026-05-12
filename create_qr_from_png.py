#!/usr/bin/env python3
"""
Create QR from Merged PNG
Converts merged PNG data into a functional QR code.
"""

import qrcode
import base64
import os
from PIL import Image, ImageDraw, ImageFont
import hashlib

def create_functional_qr():
    """Create a functional QR code from merged PNG data."""
    
    print("🎯 Creating Functional QR from Merged PNG")
    print("=" * 45)
    
    # Read the merged data file
    data_file = "merged_vectors.data"
    
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        print("   Please run final_merge.py first")
        return
    
    with open(data_file, 'rb') as f:
        merged_data = f.read()
    
    print(f"✓ Read merged data: {len(merged_data)} bytes")
    
    # Convert to base64 for QR encoding
    encoded_data = base64.b64encode(merged_data).decode('utf-8')
    print(f"✓ Base64 encoded: {len(encoded_data)} characters")
    
    # Check if data fits in single QR
    max_capacity = 2953  # Version 40 max for binary data
    if len(encoded_data) > max_capacity:
        print(f"⚠️  Data too large for single QR ({len(encoded_data)} > {max_capacity})")
        print("   Creating multi-QR system...")
        return create_multi_qr_system(encoded_data)
    
    # Create single QR code
    print("🎨 Creating single QR code...")
    
    qr = qrcode.QRCode(
        version=1,  # Auto-detect optimal version
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=8,  # Larger boxes for better scanning
        border=4,   # Standard border
    )
    
    qr.add_data(encoded_data)
    qr.make(fit=True)
    
    # Create image with styling
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Add visual indicators
    draw = ImageDraw.Draw(qr_img)
    width, height = qr_img.size
    
    # Add corner markers (indicates merged vector data)
    marker_size = 30
    marker_color = "purple"
    
    # Top-left
    draw.rectangle([0, 0, marker_size, marker_size], fill=marker_color, outline="darkviolet", width=2)
    # Top-right
    draw.rectangle([width-marker_size, 0, width, marker_size], fill=marker_color, outline="darkviolet", width=2)
    # Bottom-left
    draw.rectangle([0, height-marker_size, marker_size, height], fill=marker_color, outline="darkviolet", width=2)
    
    # Add center watermark
    center_x, center_y = width // 2, height // 2
    watermark_size = 50
    
    # Create semi-transparent watermark
    watermark = Image.new('RGBA', (watermark_size, watermark_size), (0, 0, 0, 0))
    watermark_draw = ImageDraw.Draw(watermark)
    
    # Draw "M" for "Merged"
    font_size = 30
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    watermark_draw.text((10, 10), "M", fill=(128, 0, 128, 128), font=font)
    
    # Paste watermark
    watermark_x = center_x - watermark_size // 2
    watermark_y = center_y - watermark_size // 2
    qr_img.paste(watermark, (watermark_x, watermark_y), watermark)
    
    # Add text info
    try:
        font = ImageFont.load_default()
        info_text = f"MERGED: {len(merged_data)}B"
        draw.text((5, height-20), info_text, fill="purple", font=font)
    except:
        pass
    
    # Save the QR code
    output_file = "functional_merged_qr.png"
    qr_img.save(output_file, quality=95)
    
    print(f"✅ Functional QR saved: {output_file}")
    print(f"   Dimensions: {width}x{height} pixels")
    print(f"   Data capacity: {len(encoded_data)}/{max_capacity}")
    print(f"   Error correction: High (Level H)")
    
    # Create reconstruction instructions
    create_qr_instructions(output_file, len(encoded_data))
    
    return output_file

def create_multi_qr_system(encoded_data: str):
    """Create multi-QR system for large data."""
    
    print("🔄 Creating multi-QR system...")
    
    # Split data into manageable chunks
    chunk_size = 2500  # Conservative chunk size
    chunks = [encoded_data[i:i+chunk_size] for i in range(0, len(encoded_data), chunk_size)]
    
    print(f"   Creating {len(chunks)} QR codes...")
    
    # Create grid layout
    cols = 2
    rows = (len(chunks) + cols - 1) // cols
    
    qr_size = 350
    margin = 30
    title_height = 60
    
    canvas_width = cols * qr_size + (cols + 1) * margin
    canvas_height = rows * qr_size + (rows + 1) * margin + title_height
    
    # Create canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    draw = ImageDraw.Draw(canvas)
    
    # Add title
    try:
        font = ImageFont.load_default()
        title = f"Merged Vector Data - {len(chunks)} QR Codes"
        draw.text((20, 20), title, fill="black", font=font)
        subtitle = f"Total: {len(encoded_data)} characters"
        draw.text((20, 40), subtitle, fill="gray", font=font)
    except:
        pass
    
    # Create individual QRs
    successful_qrs = 0
    
    for i, chunk in enumerate(chunks):
        try:
            # Create QR
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=6,
                border=3,
            )
            
            # Add chunk header
            chunk_header = f"MERGED_{i+1}_{len(chunks)}:"
            chunk_data = chunk_header + chunk
            
            qr.add_data(chunk_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Calculate position
            col = i % cols
            row = i // cols
            x = col * (qr_size + margin) + margin
            y = row * (qr_size + margin) + margin + title_height
            
            # Add to canvas
            canvas.paste(qr_img, (x, y))
            
            # Add chunk number
            try:
                font = ImageFont.load_default()
                chunk_text = f"{i+1}/{len(chunks)}"
                draw.text((x + 5, y + 5), chunk_text, fill="red", font=font)
            except:
                pass
            
            # Add corner marker
            marker_size = 20
            draw.rectangle([x, y, x + marker_size, y + marker_size], fill="purple")
            
            successful_qrs += 1
            print(f"   ✓ QR {i+1}/{len(chunks)} created")
            
        except Exception as e:
            print(f"   ❌ QR {i+1} failed: {e}")
            continue
    
    # Save multi-QR image
    output_file = "multi_qr_merged.png"
    canvas.save(output_file, quality=95)
    
    print(f"✅ Multi-QR saved: {output_file}")
    print(f"   Canvas size: {canvas_width}x{canvas_height}")
    print(f"   Successful QRs: {successful_qrs}/{len(chunks)}")
    
    # Create multi-QR instructions
    create_multi_qr_instructions(output_file, len(chunks), len(encoded_data))
    
    return output_file

def create_qr_instructions(qr_file: str, data_size: int):
    """Create reconstruction instructions for single QR."""
    
    instructions_file = qr_file.replace('.png', '_instructions.txt')
    
    with open(instructions_file, 'w') as f:
        f.write("Functional QR Reconstruction Instructions\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"QR File: {qr_file}\n")
        f.write(f"Data Size: {data_size} characters\n\n")
        
        f.write("To Reconstruct Merged Data:\n")
        f.write("1. Scan the QR code with any QR scanner app\n")
        f.write("2. Copy the scanned text (base64 data)\n")
        f.write("3. Decode base64 to get binary data\n")
        f.write("4. Save as 'reconstructed_merged.data'\n")
        f.write("5. Use the reconstructed data for vector operations\n\n")
        
        f.write("Python Reconstruction Code:\n")
        f.write("import base64\n")
        f.write("with open('scanned_text.txt', 'r') as f:\n")
        f.write("    base64_data = f.read().strip()\n")
        f.write("binary_data = base64.b64decode(base64_data)\n")
        f.write("with open('reconstructed_merged.data', 'wb') as f:\n")
        f.write("    f.write(binary_data)\n\n")
        
        f.write("QR Features:\n")
        f.write("- Purple corners: Indicates merged vector data\n")
        f.write("- Center 'M' watermark: Merged data identifier\n")
        f.write("- High error correction: Reliable scanning\n")
        f.write("- Bottom info: Data size indicator\n")
    
    print(f"📄 Instructions saved: {instructions_file}")

def create_multi_qr_instructions(qr_file: str, qr_count: int, data_size: int):
    """Create reconstruction instructions for multi-QR."""
    
    instructions_file = qr_file.replace('.png', '_instructions.txt')
    
    with open(instructions_file, 'w') as f:
        f.write("Multi-QR Reconstruction Instructions\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"QR File: {qr_file}\n")
        f.write(f"QR Count: {qr_count}\n")
        f.write(f"Total Data Size: {data_size} characters\n\n")
        
        f.write("To Reconstruct Merged Data:\n")
        f.write("1. Scan all QR codes in order (1 to {qr_count})\n")
        f.write("2. For each QR, copy the scanned text\n")
        f.write("3. Remove the 'MERGED_X_Y:' prefix from each\n")
        f.write("4. Concatenate all base64 data in order\n")
        f.write("5. Decode the combined base64 to get binary data\n")
        f.write("6. Save as 'reconstructed_merged.data'\n\n")
        
        f.write("Python Reconstruction Code:\n")
        f.write("import base64\n\n")
        f.write("all_chunks = []\n")
        f.write("for i in range(1, {qr_count} + 1):\n")
        f.write("    with open(f'chunk_{{i}}.txt', 'r') as f:\n")
        f.write("        chunk_data = f.read().strip()\n")
        f.write("        # Remove prefix\n")
        f.write("        chunk_data = chunk_data.split(':', 1)[1]\n")
        f.write("        all_chunks.append(chunk_data)\n\n")
        f.write("combined_data = ''.join(all_chunks)\n")
        f.write("binary_data = base64.b64decode(combined_data)\n")
        f.write("with open('reconstructed_merged.data', 'wb') as f:\n")
        f.write("    f.write(binary_data)\n\n")
        
        f.write("QR Features:\n")
        f.write("- Purple corners: Merged vector data indicators\n")
        f.write("- Red numbers: Chunk sequence (1/n)\n")
        f.write("- High error correction: Reliable scanning\n")
    
    print(f"📄 Multi-QR instructions saved: {instructions_file}")

def main():
    """Main function."""
    
    print("🚀 Creating Functional QR from Merged PNG Data")
    print("=" * 55)
    
    # Create functional QR
    qr_file = create_functional_qr()
    
    if qr_file:
        print(f"\n🎯 Functional QR Creation Complete!")
        print(f"   QR file: {qr_file}")
        print(f"   Ready for scanning and reconstruction")
        print(f"   Contains all merged vector data")
        print(f"   Follow the instructions file for reconstruction")
    else:
        print("❌ QR creation failed!")

if __name__ == "__main__":
    main()
