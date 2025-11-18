#!/usr/bin/env python3
"""
Test script to validate visualization features in Codeius AI Coding Agent
"""
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from coding_agent.visualization_manager import VisualizationManager

def test_visualization_features():
    """Test all visualization features"""
    print("Testing Visualization Features...")
    
    # Initialize the visualization manager
    vm = VisualizationManager()
    
    print("\n1. Testing Dependency Graph Visualization...")
    try:
        # Create a small test project for faster testing
        import tempfile
        import os

        # Create a temporary directory with a simple Python project
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some sample Python files with dependencies
            file1_path = os.path.join(temp_dir, "module1.py")
            with open(file1_path, "w") as f:
                f.write("# Simple module\n\ndef hello():\n    return 'Hello from module1'\n")

            file2_path = os.path.join(temp_dir, "module2.py")
            with open(file2_path, "w") as f:
                f.write("# Another module\nfrom module1 import hello\n\ndef greet():\n    return hello() + ' Greeting!'\n")

            # Generate dependency graph for the small project
            result = vm.generate_dependency_graph(temp_dir)
            print(f"   SUCCESS: {result}")
    except Exception as e:
        print(f"   ERROR: Dependency graph generation failed: {e}")

    print("\n2. Testing Project Structure Visualization...")
    try:
        result = vm.generate_project_structure()
        print(f"   SUCCESS: {result}")
    except Exception as e:
        print(f"   ERROR: Project structure generation failed: {e}")

    print("\n3. Testing Performance Dashboard...")
    try:
        result = vm.generate_performance_dashboard()
        print(f"   SUCCESS: {result}")
    except Exception as e:
        print(f"   ERROR: Performance dashboard generation failed: {e}")

    print("\n4. Verifying output directory...")
    try:
        output_dir = vm.output_path
        if output_dir.exists():
            files = list(output_dir.iterdir())
            print(f"   SUCCESS: Output directory exists with {len(files)} files:")
            for f in files:
                print(f"      - {f.name} ({f.stat().st_size} bytes)")
        else:
            print(f"   ERROR: Output directory does not exist: {output_dir}")
    except Exception as e:
        print(f"   ERROR: Output directory check failed: {e}")

    print("\nVisualization tests completed!")

if __name__ == "__main__":
    test_visualization_features()