import sys

import torch
import transformers
import datasets
import peft
import trl
import sqlglot
import networkx


def main() -> None:
    print("=" * 60)
    print("VGSR ENVIRONMENT")
    print("=" * 60)

    print(f"Python       : {sys.version.split()[0]}")
    print(f"PyTorch      : {torch.__version__}")
    print(f"Transformers : {transformers.__version__}")
    print(f"Datasets     : {datasets.__version__}")
    print(f"PEFT         : {peft.__version__}")
    print(f"TRL          : {trl.__version__}")
    print(f"SQLGlot      : {sqlglot.__version__}")
    print(f"NetworkX     : {networkx.__version__}")

    print()
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU          : {torch.cuda.get_device_name(0)}")
        print(f"CUDA version : {torch.version.cuda}")
    else:
        print("GPU          : CPU mode")

    print("=" * 60)


if __name__ == "__main__":
    main()
