"""Streamlit Community Cloud entry point.

The main application lives in ``app.py``. Streamlit Community Cloud defaults its
"Main file path" to ``streamlit_app.py``, so this thin shim runs the app without
extra configuration. You can also set the main file path to ``app.py`` directly.
"""

from app import main

if __name__ == "__main__":
    main()
