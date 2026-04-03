# config_manager.py
import os
import json

def load_system_config(file_path="config.json"):
    defaults = {
        "eqmax_dir": "C:/EqMax_Win64",
        "destinations": [],
        "ram_limit": 1024,
        "min_trigger_int": "3",
        "min_display_int": "1"
    }

    config = defaults.copy()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except:
            pass

    config["eqmax_dir"] = os.path.normpath(config["eqmax_dir"])
    config["exe_path"] = os.path.join(config["eqmax_dir"], "EqMax.exe")
    config["is_env_ok"] = os.path.exists(config["exe_path"])

    return config