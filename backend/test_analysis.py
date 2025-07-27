#!/usr/bin/env python3
import os
import json

def test_analysis_files():
    print("🔍 Testing Analysis Files...")
    
    analysis_dir = "analysis_output"
    if not os.path.exists(analysis_dir):
        print("❌ Analysis output directory not found!")
        return
    
    files = [f for f in os.listdir(analysis_dir) if f.endswith('.json')]
    print(f"📄 Found {len(files)} analysis files:")
    
    for i, file in enumerate(files):
        file_path = os.path.join(analysis_dir, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"{i+1}. {file}")
            print(f"   📅 Processed: {data.get('processed_at', 'Unknown')}")
            print(f"   📄 Filename: {data.get('filename', 'Unknown')}")
            print(f"   📊 Chunks: {len(data.get('chunks', []))}")
            
            # Check for "mamul mal stoku" in content
            full_text = data.get('content', {}).get('full_text', '')
            if 'mamul mal stoku' in full_text.lower():
                print(f"   ✅ Contains 'mamul mal stoku'")
                # Find the specific text
                if 'temmuzda artış gösterdi' in full_text.lower():
                    print(f"   🎯 Contains target text: 'temmuzda artış gösterdi'")
            else:
                print(f"   ❌ Does NOT contain 'mamul mal stoku'")
    
    # Show latest file
    if files:
        latest_file = max(files)
        print(f"\n🔄 Latest file: {latest_file}")

if __name__ == "__main__":
    test_analysis_files()
