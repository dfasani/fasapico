# fasapico
Useful stuff for the Raspi Pico (W, H, WH...)

## Installation

### Option 1: Download on the Pico (recommended)
Copy `libs/00_download_libs.py` to your Pico and run it. This will download the complete `fasapico` package and auxiliary libraries.

### Option 2: Manual copy
Copy the `fasapico/` folder to `/lib/fasapico/` on your microcontroller.

## Usage
```python
from fasapico import *

# Connect to WiFi
connect_to_wifi()

# Use the utilities
```

## Examples
Please have a look at the [example folder](examples).
