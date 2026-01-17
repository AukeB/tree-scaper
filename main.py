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
        tree_data = json.load(file)

    # Initialize TreeVisualization class.
    tree_visualizer = TreeVisualizer(tree_data, config)

    # Draw the tree.
    tree_visualizer.draw()

if __name__ == "__main__":
    main()


"""
TODO:
- Runtime parameters                                                        DONE
    - Dark/light mode -> self.dark_mode: bool = False                       DONE
        - color_palettes opsplitsen in light en dark color_palettes         DONE
        - Wat meer verschillende dark mode color palettes                   
- Laatste layer grijs                                                       DONE
    - Color palette's aanpassen (groter contrast)                           DONE
    - ColorPallete variabele in config                                      DONE
    - Aantal paletten uitbreiden                                            DONE
- Kijken waar de groootte van nodes van afhangt                             DONE
    - inzoomen/uitzoomen implementeren                                      DONE
    - Niet alleen font maar ook                                             DONE
        - margins, border widths, spacings in between                       DONE
        - aanpsseen op basis van zoom                                       DONE
    - In- and uitzoomen optimaliseren (met positie van de muis meegenomen)  
- Images in the README.md stoppen                                           
- README.md uitbreiden met features                                         
- Refactoring                                                               
    - Kijken of alles naar 2 classes kan -> measuring & draw class          
    - Misschien nog meer                                                    
- Compact mode                                                              
    Misschien de v_stacks_leafs en compact_mode mergen en dan zeggen dat    
    v_stack_leafs compact_mode level 1 is en de compact_mode wordt          
    compact_model level 2.                                                  
- Vertical alignment van dezelfde level nodes als er een node is            
    met een groter aantal regels in de title of subtitle                    
- CLI                                                                       
    - parameter in cli voor meegevben data_path naar .json file             
    - Andere runtime parameters toevoegen                                   
"""