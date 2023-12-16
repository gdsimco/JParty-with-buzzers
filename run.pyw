from jparty.main import main
import time
import os
import json
import subprocess
import signal
from jparty.constants import DEFAULT_CONFIG

# Check if config.json exists
if not os.path.exists('config.json'):
    # If not, create it with a default settings
    with open('config.json', 'w') as f:
        data = DEFAULT_CONFIG
        json.dump(data, f)

if __name__ == "__main__":
    main()