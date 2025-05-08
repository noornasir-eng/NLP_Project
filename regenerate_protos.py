import os
import subprocess

# Generate the gRPC Python files from proto
def generate_protos():
    print("Regenerating protobuf files with compatible version...")
    result = subprocess.run(
        ["python", "-m", "grpc_tools.protoc", 
         "-I.", 
         "--python_out=.", 
         "--grpc_python_out=.", 
         "agent.proto"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error regenerating proto files: {result.stderr}")
    else:
        print("Successfully regenerated proto files!")
        # Fix imports in the generated files if needed
        fix_imports()

def fix_imports():
    """Fix imports in the generated files if needed"""
    # Some versions might need import fixes, this function handles that
    for filename in ["agent_pb2.py", "agent_pb2_grpc.py"]:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                content = file.read()
            
            # Fix for newer protobuf versions
            if "runtime_version" in content:
                print(f"Fixing imports in {filename}...")
                content = content.replace(
                    "from google.protobuf import runtime_version as _runtime_version",
                    "# Removed runtime_version import for compatibility"
                )
                
                # Remove validation that uses runtime_version
                content = content.replace(
                    "_runtime_version.ValidateProtobufRuntimeVersion(",
                    "# _runtime_version.ValidateProtobufRuntimeVersion("
                )
                
                # Save the fixed file
                with open(filename, "w") as file:
                    file.write(content)
                print(f"Fixed {filename}")

if __name__ == "__main__":
    generate_protos()