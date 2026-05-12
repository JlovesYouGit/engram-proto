#!/usr/bin/env python3
"""
Merge Vectors to Single PNG
Combines qr_vector_compressed.bin and qr_pattern.bin into one optimized PNG.
"""

import qrcode
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base64
import os
import hashlib
import struct

class VectorMerger:
    """Merges multiple vector files into a single optimized PNG."""
    
    def __init__(self):
        self.merged_data = b''
        self.metadata = {}
        
    def read_vector_file(self, filename: str) -> bytes:
        """Read and parse vector file."""
        
        print(f"📖 Reading vector file: {filename}")
        
        if not os.path.exists(filename):
            print(f"❌ File not found: {filename}")
            return b''
            
        with open(filename, 'rb') as f:
            data = f.read()
        
        print(f"   Size: {len(data)} bytes")
        
        # Parse header if it's a QRVC file
        if data.startswith(b'QRVC'):
            header_size = 17
            qr_size = int.from_bytes(data[5:9], 'big')
            logic_size = int.from_bytes(data[9:13], 'big')
            
            print(f"   Header: QRVC v{data[4]}")
            print(f"   QR Pattern: {qr_size} bytes")
            print(f"   Logic Data: {logic_size} bytes")
            
            # Extract components
            qr_pattern = data[header_size:header_size+qr_size]
            logic_data = data[header_size+qr_size:]
            
            return qr_pattern + logic_data
        else:
            # Treat as raw binary data
            return data
    
    def merge_vectors(self, vector_files: list) -> bytes:
        """Merge multiple vector files into single data stream."""
        
        print(f"🔗 Merging {len(vector_files)} vector files...")
        
        merged_data = b''
        file_info = []
        
        for i, filename in enumerate(vector_files):
            file_data = self.read_vector_file(filename)
            
            if file_data:
                # Add file header
                file_header = struct.pack('I', len(file_data))  # 4 bytes size
                file_hash = hashlib.md5(file_data).digest()[:4]  # 4 bytes hash
                
                merged_data += file_header + file_hash + file_data
                
                file_info.append({
                    'index': i,
                    'filename': filename,
                    'size': len(file_data),
                    'hash': file_hash.hex()
                })
                
                print(f"   ✓ Added {filename}: {len(file_data)} bytes")
        
        self.metadata = {
            'total_files': len(vector_files),
            'total_size': len(merged_data),
            'file_info': file_info
        }
        
        print(f"✅ Merged data: {len(merged_data)} bytes")
        return merged_data
    
    def create_advanced_qr(self, data: bytes, output_file: str = "merged_vector.png") -> str:
        """Create advanced QR code with merged data."""
        
        print(f"🎨 Creating advanced QR code...")
        
        # Convert to base64
        encoded_data = base64.b64encode(data).decode('utf-8')
        print(f"   Base64 size: {len(encoded_data)} characters")
        
        # Check if we need multi-QR approach
        max_single_capacity = 2953  # Version 40 max
        if len(encoded_data) > max_single_capacity:
            print(f"   Data too large for single QR, using multi-QR approach...")
            return self.create_multi_qr(encoded_data, output_file)
        
        # Create high-capacity QR with custom styling
        qr = qrcode.QRCode(
            version=1,  # Let it auto-determine the optimal version
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=6,  # Larger boxes for better readability
            border=6,   # Larger border
        )
        
        qr.add_data(encoded_data)
        qr.make(fit=True)
        
        # Create image with custom styling
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Add visual enhancements
        self._add_visual_indicators(qr_img, len(data), len(encoded_data))
        
        # Save the image
        qr_img.save(output_file, quality=95)
        
        print(f"✅ Advanced QR saved as: {output_file}")
        print(f"   Dimensions: {qr_img.size}")
        print(f"   Data capacity: {len(encoded_data)}/{max_single_capacity}")
        
        return output_file
    
    def create_multi_qr(self, encoded_data: str, base_output: str) -> str:
        """Create multi-QR system for large data."""
        
        # Split data into optimal chunks
        chunk_size = 2000  # Smaller chunks to fit in QR capacity
        chunks = [encoded_data[i:i+chunk_size] for i in range(0, len(encoded_data), chunk_size)]
        
        print(f"   Creating {len(chunks)} QR codes...")
        
        # Create grid layout for multiple QRs
        cols = 2 if len(chunks) > 1 else 1
        rows = (len(chunks) + cols - 1) // cols
        
        qr_size = 300  # Size of each individual QR
        margin = 20
        canvas_width = cols * qr_size + (cols + 1) * margin
        canvas_height = rows * qr_size + (rows + 1) * margin
        
        # Create canvas
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        draw = ImageDraw.Draw(canvas)
        
        qr_files = []
        
        for i, chunk in enumerate(chunks):
            # Create individual QR
            qr = qrcode.QRCode(
                version=1,  # Let it auto-determine the version
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=4,
                border=2,
            )
            
            # Add chunk header
            chunk_header = f"CHUNK_{i+1}_{len(chunks)}:"
            chunk_data = chunk_header + chunk
            
            qr.add_data(chunk_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Calculate position in grid
            col = i % cols
            row = i // cols
            x = col * (qr_size + margin) + margin
            y = row * (qr_size + margin) + margin
            
            # Paste onto canvas
            canvas.paste(qr_img, (x, y))
            
            # Add chunk number
            try:
                font = ImageFont.load_default()
                draw.text((x + 5, y + 5), f"{i+1}/{len(chunks)}", fill="red", font=font)
            except:
                draw.text((x + 5, y + 5), f"{i+1}/{len(chunks)}", fill="red")
            
            qr_files.append(f"{base_output}_part{i+1}.png")
        
        # Add title and metadata
        try:
            font = ImageFont.load_default()
            title = f"Merged Vector Data - {len(chunks)} Parts"
            draw.text((10, 5), title, fill="black", font=font)
            
            # Add file info
            y_offset = 25
            for file_info in self.metadata.get('file_info', [])[:3]:  # Show first 3 files
                info_text = f"{file_info['filename']}: {file_info['size']} bytes"
                draw.text((10, y_offset), info_text, fill="gray", font=font)
                y_offset += 15
                
            if len(self.metadata.get('file_info', [])) > 3:
                draw.text((10, y_offset), f"... and {len(self.metadata['file_info']) - 3} more", fill="gray", font=font)
        except:
            pass
        
        # Save merged image
        canvas.save(base_output, quality=95)
        
        print(f"✅ Multi-QR saved as: {base_output}")
        print(f"   Canvas size: {canvas_width}x{canvas_height}")
        print(f"   Individual QRs: {len(chunks)}")
        
        return base_output
    
    def _add_visual_indicators(self, img: Image.Image, data_size: int, encoded_size: int):
        """Add visual indicators to QR code."""
        
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Add corner indicators (showing this contains merged vectors)
        indicator_size = 30
        indicator_color = "blue"
        
        # Top-left
        draw.rectangle([0, 0, indicator_size, indicator_size], fill=indicator_color, outline="darkblue", width=2)
        # Top-right
        draw.rectangle([width-indicator_size, 0, width, indicator_size], fill=indicator_color, outline="darkblue", width=2)
        # Bottom-left
        draw.rectangle([0, height-indicator_size, indicator_size, height], fill=indicator_color, outline="darkblue", width=2)
        
        # Add data info in corners
        try:
            font = ImageFont.load_default()
            
            # Top-left info
            draw.text((5, 5), f"{data_size}B", fill="white", font=font)
            # Top-right info
            draw.text((width-25, 5), f"MERGE", fill="white", font=font)
            # Bottom-left info
            draw.text((5, height-15), f"QRVC", fill="white", font=font)
            
        except:
            pass
        
        # Add center watermark
        center_x, center_y = width // 2, height // 2
        watermark_size = 40
        
        # Create semi-transparent watermark
        watermark = Image.new('RGBA', (watermark_size, watermark_size), (0, 0, 0, 0))
        watermark_draw = ImageDraw.Draw(watermark)
        watermark_draw.ellipse([0, 0, watermark_size, watermark_size], fill=(0, 0, 255, 64))
        
        # Paste watermark
        watermark_x = center_x - watermark_size // 2
        watermark_y = center_y - watermark_size // 2
        img.paste(watermark, (watermark_x, watermark_y), watermark)
    
    def create_info_file(self, output_file: str):
        """Create information file for the merged QR."""
        
        info_file = output_file.replace('.png', '_info.txt')
        
        with open(info_file, 'w') as f:
            f.write("Merged Vector QR Information\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Output File: {output_file}\n")
            f.write(f"Total Files Merged: {self.metadata.get('total_files', 0)}\n")
            f.write(f"Total Data Size: {self.metadata.get('total_size', 0)} bytes\n\n")
            
            f.write("Merged Files:\n")
            for file_info in self.metadata.get('file_info', []):
                f.write(f"  {file_info['index'] + 1}. {file_info['filename']}\n")
                f.write(f"     Size: {file_info['size']} bytes\n")
                f.write(f"     Hash: {file_info['hash']}\n")
            
            f.write(f"\nQR Code Features:\n")
            f.write(f"  - Version 40 (maximum capacity)\n")
            f.write(f"  - High error correction (Level H)\n")
            f.write(f"  - Blue corner indicators (merged data)\n")
            f.write(f"  - Center watermark (vector data)\n")
            f.write(f"  - Base64 encoded binary data\n\n")
            
            f.write("Reconstruction Instructions:\n")
            f.write("1. Scan the QR code\n")
            f.write("2. Decode base64 to get binary data\n")
            f.write("3. Parse file headers to extract individual vectors\n")
            f.write("4. Verify MD5 checksums for each file\n")
            f.write("5. Reconstruct original vector files\n")
        
        print(f"📄 Info file saved as: {info_file}")

def main():
    """Main function to merge vectors into single PNG."""
    
    print("🚀 Merging Vectors to Single PNG")
    print("=" * 50)
    
    # Initialize merger
    merger = VectorMerger()
    
    # Define vector files to merge
    vector_files = [
        "qr_vector_compressed.bin",
        "qr_pattern.bin"
    ]
    
    # Check if files exist
    existing_files = []
    for filename in vector_files:
        if os.path.exists(filename):
            existing_files.append(filename)
            print(f"✓ Found: {filename}")
        else:
            print(f"❌ Missing: {filename}")
    
    if not existing_files:
        print("❌ No vector files found to merge!")
        return 1
    
    # Merge vectors
    merged_data = merger.merge_vectors(existing_files)
    
    if not merged_data:
        print("❌ Failed to merge vectors!")
        return 1
    
    # Create QR code
    output_file = "merged_vectors.png"
    qr_file = merger.create_advanced_qr(merged_data, output_file)
    
    # Create info file
    merger.create_info_file(qr_file)
    
    print(f"\n🎯 Vector Merge Complete!")
    print(f"   Merged {len(existing_files)} files into single QR")
    print(f"   Total data: {len(merged_data)} bytes")
    print(f"   Output: {qr_file}")
    print(f"   Ready for scanning and reconstruction!")
    
    return 0

if __name__ == "__main__":
    exit(main())
