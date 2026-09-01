import sys
from pathlib import Path


MANAGER_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MANAGER_ROOT))

from monitor_application import MissionMonitor


def main() -> None:
    app = MissionMonitor()
    app.run()


if __name__ == "__main__":
    main()
