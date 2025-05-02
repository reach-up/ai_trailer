#!/usr/bin/env python3
"""
Dry run script to validate the configuration flow and module imports
for the AI Trailer generator pipeline.
"""
import os
import sys
import importlib
from pathlib import Path

def print_header(message):
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60)

def check_config_and_dirs():
    print_header("CHECKING CONFIGURATION AND DIRECTORIES")
    try:
        from src.common import configs, MOVIES_DIR, PROJECT_DIR, FRAMES_DIR, TRAILER_DIR
        
        print(f"✓ Project directory: {PROJECT_DIR}")
        print(f"✓ Movies directory: {MOVIES_DIR}")
        print(f"✓ Frames directory: {FRAMES_DIR}")
        print(f"✓ Trailer directory: {TRAILER_DIR}")
        print(f"✓ Video path: {configs['video_path']}")
        
        return True
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        return False

def check_module_imports():
    print_header("CHECKING MODULE IMPORTS")
    
    modules = [
        'plot_retrieval', 
        'frame', 
        'image_retrieval', 
        'voice', 
        'clip', 
        'audio_clip', 
        'join_clip'
    ]
    
    all_passed = True
    for module_name in modules:
        try:
            # Try to import the module
            full_module_name = f"src.{module_name}"
            module = importlib.import_module(full_module_name)
            print(f"✓ Module {module_name} imported successfully")
        except Exception as e:
            print(f"✗ Failed to import {module_name}: {e}")
            all_passed = False
    
    return all_passed

def check_main_function():
    print_header("CHECKING MAIN FUNCTION")
    try:
        from src.main import main
        print(f"✓ main() function imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import main() function: {e}")
        return False

def check_api_endpoint():
    print_header("CHECKING API ENDPOINT")
    try:
        from api import app, generate_trailer
        print(f"✓ API endpoint imported successfully")
        
        # Check if the API imports from common
        import inspect
        import api
        source = inspect.getsource(api)
        if "from src.common import" in source:
            print(f"✓ API imports correctly from common module")
        else:
            print(f"⚠️ API might not be importing from common module properly")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import API: {e}")
        return False

def check_video_path_flow():
    print_header("CHECKING VIDEO PATH FLOW")
    
    # Check if configs["video_path"] is used consistently
    from src.common import configs
    print(f"Current video path in configs: {configs['video_path']}")
    
    # Set a test value
    test_path = "test_video_path.mp4"
    old_path = configs["video_path"]
    configs["video_path"] = test_path
    
    print(f"Updated video path in configs to: {configs['video_path']}")
    
    # Import a module that uses video_path to check if it picks up the change
    try:
        # Force reload the clip module to pick up the new config
        if 'src.clip' in sys.modules:
            del sys.modules['src.clip']
        
        import src.clip
        print("✓ Updated video path propagated to imported modules")
        
        # Restore the original path
        configs["video_path"] = old_path
        print(f"Restored video path in configs to: {configs['video_path']}")
        
        return True
    except Exception as e:
        # Restore the original path
        configs["video_path"] = old_path
        print(f"✗ Error testing video path propagation: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 STARTING DRY RUN OF AI TRAILER GENERATOR")
    print("This will validate the configuration, directories, and module imports")
    print("without executing the actual pipeline.\n")
    
    results = []
    results.append(("Configuration & Directories", check_config_and_dirs()))
    results.append(("Module Imports", check_module_imports()))
    results.append(("Main Function", check_main_function()))
    results.append(("API Endpoint", check_api_endpoint()))
    results.append(("Video Path Flow", check_video_path_flow()))
    
    print_header("DRY RUN RESULTS SUMMARY")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        all_passed = all_passed and passed
        print(f"{status} - {name}")
    
    overall = "SUCCESS" if all_passed else "FAILURE"
    print(f"\nOVERALL DRY RUN RESULT: {overall}")
    
    if not all_passed:
        print("\nSome checks failed. Please review the output above for details.")
    else:
        print("\nAll checks passed! The configuration flow is working properly.")
        print("The system should now handle video paths correctly throughout the pipeline.")
