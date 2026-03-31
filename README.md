# Recipe-Conversion
This is a lightweight Python tool for converting recipe ingredient units between volume (cups, tbsp, tsp, oz) and weight (grams), with support for fractional quantities, scaling, and multi-section recipes. 

## Features
- Convert between:
  - Volume → Weight
  - Weight → Volume
- Supports:
  - Mixed fractions ("1 1/2 cups")
  - Decimals ("1.5 cups")
- Automatically:
  - Parses ingredient strings
  - Handles "of" syntax ("1 cup of sugar")
- Recipe-level features:
  - Supports multi-section recipes (e.g. "For the frosting:")
  - Preserves formatting and structure
- Customizations:
  - Scale recipes (e.g. double or halve)
  - Exclude specific ingredients from conversion

## Repository Structure
```
├── convert_recipe.py                          # Core conversion functions
├── king_arthur_ingredient_weights2.csv        # Ingredient conversion table
├── chocolate_pan_cake_weight.txt              # example recipe in weight measurements
├── chocolate_pan_cake_volume.txt              # example recipe in volume measurements
└── README.md
```

## Ingredient conversion data
The file king_arthur_ingredient_weights2.csv contains conversion factors for each ingredient, sourced from https://www.kingarthurbaking.com/learn/ingredient-weight-chart

Feel free to add ingredients to your version, including common ways that you write ingredients, following the structure below. The code is spelling-sensitive.

Note that:
- "sugar"/"white sugar"/"granulated sugar" all work for "white granulated sugar"
- "AP flour" also works for "All-Purpose Flour"


#### Columns:
| Column Name    | Description                 |
| -------------- | --------------------------- |
| INGREDIENT     | Ingredient name (UPPERCASE) |
| GRAMS_PER_CUP  | Grams per cup               |
| GRAMS_PER_TBSP | Grams per tablespoon        |
| GRAMS_PER_TSP  | Grams per teaspoon          |


#### Example
INGREDIENT,GRAMS_PER_CUP,GRAMS_PER_TBSP,GRAMS_PER_TSP
SUGAR,200,12.5,4.2
FLOUR,120,7.5,2.5
BUTTER,227,14.2,4.7

## Installation
Clone the repository:
`git clone https://github.com/yourusername/recipe-converter.git
cd recipe-converter`

Install dependencies:
`pip install numpy pandas`

## Usage
Import functions
`from recipe_converter import convert_recipe`

Convert a recipe
`converted = convert_recipe("chocolate_pan_cake_volume.txt")
print("\n".join(converted))`

Convert to cups
`converted = convert_recipe("chocolate_pan_cake_weight.txt", toCups = True)`

Scale a recipe
`converted = convert_recipe("chocolate_pan_cake_volume.txt", scaling = 2)`

Exclude ingredients
`converted = convert_recipe(
    "chocolate_pan_cake_volume.txt",
    exclude=["salt", "granulated sugar"]
)`

## How it Works
1) Parsing
   - Split ingredient strings into quantity, unit, ingredient name
2) Lookup
   - Matches ingredient to King Arthur Ingredient Weight Chart
3) Conversion
   - Uses grams ↔ tsp ↔ tbsp ↔ cups
   - Outputs clean fractional measurements when possible
4) Formatting
   - Returns readable ingredient strings

## Limitations
- Ingredient names must match those in king_arthur_ingredient_weights2.csv
- Section detection is heuristic based, lines without numbers are treated as headers
- Does not currently support:
-   units like "pinch", "dash", "to taste"
-   Complex ingredient descriptions

## Future improvements
- Better natural language parsing
- support for more units
- GUI or web interface
- Ingredient alias matching

## Contributing
Pull requests are welcome! If you’d like to add:
- More ingredients
- Better parsing logic
- New features
feel free to contribute.
 
