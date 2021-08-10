# selen

```
Xvfb :19 -screen 0 800x600x8
NO_AT_BRIDGE=1 xvfb-run WebKitWebDriver --host=0.0.0.0 --port=4444

LOG_LEVEL=debug python3 run.py
```
