import sys
print(f"Python version: {sys.version}")

try:
    from cerebras.cloud.sdk import Cerebras
    print("Cerebras SDK imported successfully")
except ImportError as e:
    print(f"Failed to import Cerebras SDK: {e}")

try:
    from gpt_index import GPTIndex
    print("GPTIndex imported successfully")
except ImportError as e:
    print(f"Failed to import GPTIndex: {e}")

try:
    from llama_index import LlamaIndex
    print("LlamaIndex imported successfully")
except ImportError as e:
    print(f"Failed to import LlamaIndex: {e}")

try:
    import yaml
    print("YAML imported successfully")
except ImportError as e:
    print(f"Failed to import YAML: {e}")

try:
    import typing_extensions
    print(f"typing_extensions imported successfully, version: {typing_extensions.__version__}")
except ImportError as e:
    print(f"Failed to import typing_extensions: {e}")
except AttributeError:
    print("typing_extensions imported but version not available") 