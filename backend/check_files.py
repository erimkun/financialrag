#!/usr/bin/env python3
import os

def check_file_locations():
    print("🔍 Checking file locations...")
    
    # Check uploads directory
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        print(f"\n📁 UPLOADS Directory ({uploads_dir}):")
        print(f"   📊 Count: {len(files)}")
        for file in files:
            file_path = os.path.join(uploads_dir, file)
            size = os.path.getsize(file_path)
            print(f"   - {file} ({size} bytes)")
    else:
        print(f"❌ Uploads directory not found: {uploads_dir}")
    
    # Check analysis_output directory
    analysis_dir = "analysis_output"
    if os.path.exists(analysis_dir):
        files = [f for f in os.listdir(analysis_dir) if f.endswith('.json')]
        print(f"\n📁 ANALYSIS_OUTPUT Directory ({analysis_dir}):")
        print(f"   📊 Count: {len(files)}")
        for file in files:
            file_path = os.path.join(analysis_dir, file)
            mod_time = os.path.getmtime(file_path)
            import datetime
            mod_date = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"   - {file} (Modified: {mod_date})")
    else:
        print(f"❌ Analysis directory not found: {analysis_dir}")
    
    # Check documents folder (user mentioned)
    documents_dir = "../documents"
    if os.path.exists(documents_dir):
        files = [f for f in os.listdir(documents_dir) if f.endswith('.pdf')]
        print(f"\n📁 DOCUMENTS Directory ({documents_dir}):")
        print(f"   📊 Count: {len(files)}")
        for file in files:
            print(f"   - {file}")
    else:
        print(f"❌ Documents directory not found: {documents_dir}")

if __name__ == "__main__":
    check_file_locations()
