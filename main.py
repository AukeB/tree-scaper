"""Main module."""

def main():
    """Main function."""
    # Imports
    import json
    from src.tree_scaper.config_manager import ConfigManager
    from src.tree_scaper.tree_visualizer import TreeVisualizer
    from src.tree_scaper.constants import DATA_PATH

    # Load main configuration file
    config_manager = ConfigManager()
    config = config_manager.load_config_file()

    # Load data.
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Initialize TreeVisualization class.
    tree_visualizer = TreeVisualizer(data, config)

    # Draw the tree.
    tree_visualizer.draw()

if __name__ == "__main__":
    main()