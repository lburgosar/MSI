import sys
from pathlib import Path


MANAGER_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MANAGER_ROOT))

from core.application import MissionStudio


def main() -> None:
    app = MissionStudio()
    app.run()


if __name__ == "__main__":
    main()
