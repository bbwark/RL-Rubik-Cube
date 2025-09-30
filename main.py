#!/usr/bin/env python3
"""
Main entry point for the RL-Rubik-Cube project.

This script provides easy access to different components of the project:
- Run tests
- Launch playground  
- Future: training, agent demonstration, etc.
"""

import sys
import argparse

def run_tests():
    """Run the cube tests."""
    print("=== Running Cube Tests ===")
    
    from environment.test import main as test_main
    try:
        test_main()
        print("\n All tests completed successfully!")
        return True
    except Exception as e:
        print(f"\n Tests failed: {e}")
        return False

def run_playground():
    """Run the 3D cube playground."""
    print("=== Launching 3D Cube Playground ===")
    
    try:
        from utils.playground import main as playground_main
        playground_main()
        return True
    except ImportError as e:
        print(f"Could not import playground: {e}")
        print("Make sure you have the required dependencies installed:")
        print("  pip install pygame PyOpenGL PyOpenGL_accelerate")
        return False
    except Exception as e:
        print(f"Playground failed: {e}")
        return False

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="RL-Rubik-Cube Project Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py test       # Run cube tests
  python main.py playground # Launch 3D playground
  python main.py --help     # Show this help
        """
    )
    
    parser.add_argument(
        'command', 
        choices=['test', 'playground'],
        help='Command to run'
    )
    
    if len(sys.argv) == 1:
        print("=== RL-Rubik-Cube Project ===")
        print("1. Run Tests")
        print("2. Launch 3D Playground")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\nSelect option (0-2): ").strip()
                if choice == '0':
                    print("Goodbye!")
                    return
                elif choice == '1':
                    run_tests()
                    return
                elif choice == '2':
                    run_playground()
                    return
                else:
                    print("Invalid choice. Please enter 0, 1, or 2.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                return
            except EOFError:
                print("\nGoodbye!")
                return
    
    args = parser.parse_args()
    
    if args.command == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.command == 'playground':
        success = run_playground()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()