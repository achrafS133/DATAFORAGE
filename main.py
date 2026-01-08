import sys
import argparse
import yaml
from ui.tui_app import DataForgeApp

def load_config(config_path="config/settings.yaml"):
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found at {config_path}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="DataForge - High Performance DB Seeder")
    parser.add_argument("--config", type=str, default="config/settings.yaml", help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)
    
    # Initialize App
    app = DataForgeApp()
    app.run()

if __name__ == "__main__":
    main()
