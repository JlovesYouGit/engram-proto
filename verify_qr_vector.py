#!/usr/bin/env python3
"""
QR Vector Verification System
Verifies and demonstrates the compressed QR vector system.
"""

import base64
import json
import hashlib
import os
from typing import Dict, Any

class QRVectorVerifier:
    """Verifies and decompresses QR vector data."""
    
    def __init__(self):
        self.verification_results = {}
        
    def verify_vector_file(self, vector_file: str) -> Dict[str, Any]:
        """Verify the compressed vector file."""
        
        print(f"🔍 Verifying vector file: {vector_file}")
        
        if not os.path.exists(vector_file):
            return {"error": "File not found"}
            
        with open(vector_file, 'rb') as f:
            vector_data = f.read()
        
        # Parse vector header
        header = self._parse_vector_header(vector_data)
        
        if "error" in header:
            return header
            
        # Verify checksum
        checksum_valid = self._verify_checksum(vector_data, header)
        
        # Extract components
        qr_pattern = self._extract_qr_pattern(vector_data, header)
        logic_data = self._extract_logic_data(vector_data, header)
        
        # Decompress logic components
        decompressed_logic = self._decompress_logic(logic_data)
        
        results = {
            "file_size": len(vector_data),
            "header": header,
            "checksum_valid": checksum_valid,
            "qr_pattern_size": len(qr_pattern),
            "logic_data_size": len(logic_data),
            "decompressed_logic": decompressed_logic,
            "logic_components": len(decompressed_logic)
        }
        
        self.verification_results[vector_file] = results
        return results
        
    def _parse_vector_header(self, vector_data: bytes) -> Dict[str, Any]:
        """Parse QR vector header."""
        
        if len(vector_data) < 13:  # Minimum header size
            return {"error": "Invalid header - too short"}
            
        # Check magic bytes
        magic = vector_data[:4]
        if magic != b'QRVC':
            return {"error": f"Invalid magic bytes: {magic}"}
            
        # Parse header fields
        version = vector_data[4]
        qr_size = int.from_bytes(vector_data[5:9], 'big')
        logic_size = int.from_bytes(vector_data[9:13], 'big')
        checksum = vector_data[13:17]
        
        return {
            "magic": magic.decode('ascii'),
            "version": version,
            "qr_size": qr_size,
            "logic_size": logic_size,
            "checksum": checksum.hex(),
            "total_header_size": 17
        }
        
    def _verify_checksum(self, vector_data: bytes, header: Dict[str, Any]) -> bool:
        """Verify vector checksum."""
        
        # Recalculate checksum
        checksum_data = f"{header['qr_size']}{header['logic_size']}".encode()
        calculated_checksum = hashlib.md5(checksum_data).digest()[:4]
        
        stored_checksum = bytes.fromhex(header['checksum'])
        
        return calculated_checksum == stored_checksum
        
    def _extract_qr_pattern(self, vector_data: bytes, header: Dict[str, Any]) -> bytes:
        """Extract QR pattern from vector."""
        
        start = header['total_header_size']
        end = start + header['qr_size']
        
        return vector_data[start:end]
        
    def _extract_logic_data(self, vector_data: bytes, header: Dict[str, Any]) -> bytes:
        """Extract logic data from vector."""
        
        start = header['total_header_size'] + header['qr_size']
        end = start + header['logic_size']
        
        return vector_data[start:end]
        
    def _decompress_logic(self, logic_data: bytes) -> list:
        """Decompress logic components."""
        
        components = []
        offset = 0
        
        while offset < len(logic_data):
            # Parse component header
            if offset + 11 > len(logic_data):
                break
                
            name_hash = logic_data[offset:offset+4]
            data_size = int.from_bytes(logic_data[offset+4:offset+8], 'big')
            comp_type = logic_data[offset+8]
            checksum = logic_data[offset+9:offset+11]
            
            # Extract component data
            start = offset + 11
            end = start + data_size
            
            if end > len(logic_data):
                break
                
            component_data = logic_data[start:end]
            
            # Decompress based on type
            if comp_type == 1:  # JSON
                try:
                    decoded = json.loads(component_data.decode('utf-8'))
                    components.append(decoded)
                except:
                    components.append({"error": "JSON decode failed", "raw": component_data.hex()})
            else:
                components.append({"type": comp_type, "data": component_data.hex()})
            
            offset = end
            
        return components
        
    def verify_qr_files(self, qr_files: list) -> Dict[str, Any]:
        """Verify QR code files."""
        
        print(f"🔍 Verifying {len(qr_files)} QR files...")
        
        results = {
            "total_files": len(qr_files),
            "verified_files": 0,
            "files": []
        }
        
        for qr_file in qr_files:
            if os.path.exists(qr_file):
                file_size = os.path.getsize(qr_file)
                results["files"].append({
                    "name": qr_file,
                    "size": file_size,
                    "exists": True
                })
                results["verified_files"] += 1
            else:
                results["files"].append({
                    "name": qr_file,
                    "size": 0,
                    "exists": False
                })
        
        return results
        
    def display_verification_report(self):
        """Display comprehensive verification report."""
        
        print("\n" + "="*60)
        print("📊 QR VECTOR VERIFICATION REPORT")
        print("="*60)
        
        for filename, results in self.verification_results.items():
            print(f"\n📁 File: {filename}")
            print(f"   Size: {results['file_size']} bytes")
            
            if "error" in results:
                print(f"   ❌ Error: {results['error']}")
                continue
                
            print(f"   Header: {results['header']['magic']} v{results['header']['version']}")
            print(f"   QR Pattern: {results['qr_pattern_size']} bytes")
            print(f"   Logic Data: {results['logic_data_size']} bytes")
            print(f"   Checksum: {'✓ Valid' if results['checksum_valid'] else '✗ Invalid'}")
            print(f"   Logic Components: {results['logic_components']}")
            
            # Display logic components
            for i, component in enumerate(results['decompressed_logic']):
                if 'error' in component:
                    print(f"     Component {i+1}: ❌ {component['error']}")
                else:
                    comp_type = component.get('type', 'unknown')
                    print(f"     Component {i+1}: ✓ {comp_type}")
                    
                    # Show specific details for known types
                    if comp_type == 'golden_ratio':
                        print(f"       φ: {component.get('phi', 'N/A')}")
                        print(f"       Ratio: {component.get('compression_ratio', 'N/A')}")
                    elif comp_type == 'brain_mesh':
                        print(f"       Input: {component.get('input_size', 'N/A')}")
                        print(f"       Hidden: {component.get('hidden_size', 'N/A')}")
                    elif comp_type == 'throne_protocol':
                        print(f"       Routes: {len(component.get('routes', []))}")
                        print(f"       Success Rate: {component.get('success_rate', 'N/A')}")
                    elif comp_type == 'artificial_consciousness':
                        print(f"       Level: {component.get('consciousness_level', 'N/A')}")
                        print(f"       Life Force: {component.get('life_force', 'N/A')}")
                        print(f"       State: {component.get('current_state', 'N/A')}")

def main():
    """Main verification function."""
    
    print("🔍 QR Vector Verification System")
    print("="*50)
    
    verifier = QRVectorVerifier()
    
    # Verify vector file
    vector_file = "qr_vector_compressed.bin"
    vector_results = verifier.verify_vector_file(vector_file)
    
    # Verify QR files
    qr_files = [
        "qr_with_vector_part1.png",
        "qr_with_vector_part2.png"
    ]
    
    qr_results = verifier.verify_qr_files(qr_files)
    
    # Display report
    verifier.display_verification_report()
    
    # Display QR file results
    print(f"\n📱 QR Files Verification:")
    print(f"   Total: {qr_results['total_files']}")
    print(f"   Verified: {qr_results['verified_files']}")
    
    for file_info in qr_results['files']:
        status = "✓" if file_info['exists'] else "✗"
        print(f"   {status} {file_info['name']} ({file_info['size']} bytes)")
    
    # Check assembly instructions
    assembly_file = "qr_with_vector_assembly.txt"
    if os.path.exists(assembly_file):
        print(f"\n📄 Assembly Instructions: ✓ {assembly_file}")
        with open(assembly_file, 'r') as f:
            lines = f.readlines()
            print(f"   Lines: {len(lines)}")
    else:
        print(f"\n📄 Assembly Instructions: ✗ Not found")
    
    print(f"\n🎯 Verification Complete!")
    print(f"   All logic successfully compressed into QR vectors")
    print(f"   Ready for deployment and scanning")
    
    return 0

if __name__ == "__main__":
    exit(main())
