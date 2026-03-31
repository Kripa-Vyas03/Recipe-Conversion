import numpy as np
import pandas as pd
from fractions import Fraction

df = pd.read_csv("king_arthur_ingredient_weights2.csv")

def is_section_header(line):
    """
    Determine whether a line is a section header.

    A line is considered a header if:
        - It is empty
        - It ends with a colon (":")
        - It contains no numeric characters (heuristic)

    Parameters
    ----------
    line : str

    Returns
    -------
    bool
    
    """
    stripped = line.strip()

    if not stripped:
        return True

    if stripped.endswith(":"):
        return True

    if not any(char.isdigit() for char in stripped):
        return True

    return False

def make_quant_mask(lst):
    '''
    Makes boolean mask of a list of strings, where True is a quantity (float, integer, fraction)
    
    The function checks if each element in the list is an integer/float. If so, the mask element is True. If not, it checks if the element is a fraction (there are two numbers split by a slash, with a demoninator not equal to 0). If so, the mask element is True. If both checks fail, the mask element is False.
    
    Parameters
    ----------
    lst : list (strings)
        Checks which strings are Fractions/floats/integers

    Returns
    -------
    array (bool)
        Mask specifying location of Fractions/floats/integers.
        
    Examples
    --------
        >>> make_quant_mask(["hello", "there", "are", "1", "1/2", "ducks"])
            [False, False, False, True, True, False]

    '''
    frac_mask = []
    for s in lst:
        try:
            float(s)                # check if float/integer
            frac_mask.append(True)
            
        except:            
            values = s.split('/')
            # Check if there are exactly two parts, and both are composed of only digits
            if len(values) == 2 and all(i.isdigit() for i in values):
                # Also ensure the denominator is not zero
                if values[1] != '0':
                    frac_mask.append(True)
            else:
                frac_mask.append(False)

    return np.array(frac_mask)


def format_num(num, valid_frac):
    """
    Convert a float into a mixed number string using a predefined set of valid fractions.

    The function separates the input number into its whole and fractional parts.
    If the fractional part matches one of the allowed fractions, it is converted
    into a string representation (e.g., "1/4", "1/2"). The result is then returned
    as a mixed number (e.g., "1 1/4").

    If the fractional part is not in the list of valid fractions, the original
    number is returned as a string.

    Parameters
    ----------
        num (float): The number to format.

    Returns
    -------
        str: A string representation of the number as a mixed fraction if valid,
             otherwise the original number as a string.

    Examples
    --------
        >>> format_num(1.25)
        '1 1/4'
        >>> format_num(0.5)
        '1/2'
        >>> format_num(2.0)
        '2'
        >>> format_num(1.2)
        '1.2'
    """
    
    whole = int(num)
    decimal = round(num - whole, 2)  # limit keeps it clean

    if decimal in valid_frac:
        if decimal == 0:
            return str(whole)
        elif whole == 0:
            return Fraction(decimal).limit_denominator(10)
        else:
            return f"{whole} {Fraction(decimal)}"
    else:
        return str(num)

valid_frac_cups = [0.0, 0.25, 0.5, 0.75, 0.33, 0.66]
valid_frac_tbsp = np.arange(0, 1, 1/8)



def convert_ingredient(amount_ingredient, exclude, toCups, scaling = 1):
    '''
    Convert a recipe ingredient string between volume and weight units, optionally scaling the quantity. 
    
    The function parses a string contained an ingredient quantity, measurement, and name (e.g. "1 1/2 cups sugar") and converts between weight (grams) and volume (cups, tablespoons, teaspoons) using lookup values from a reference dataframe (King Arthur Ingredient Weight Chart)
    
    Special Cases:
    - ingredients like "egg" and "yolk" are not converted between units, they are only scaled numerically
    - Ingredients not found in the King Arthur Ingredient Weight Chart are not converted, only numerically scaled
    
   Parameters
   ----------
   amount_ingredient : str
        Ingredient string with quantity, measurement, and name. Accepted formats include:
            - "1.5 cups sugar"
            - "1 1/2 cups sugar"
            - "1.5 cups of sugar"
            - "1 1/2 cups of sugar"
            - "297 g sugar"
            - "297 g of sugar"
        * note that improper fractions (3/2) will not be converted -- future update
        
    exlude : list [str]
        List of ingredient names to exclude from conversion. These will only be scaled, not converted.
        
    toCups : bool
        Direction of conversion:
            - True: convert from weight (grams) → volume (cups/tbsp/tsp)
            - False: convert from volume (cups/tbsp/tsp) → weight (grams)

    scaling : float, optional (default=1)
        Factor to scale the ingredient quantity. Must be positive.
   
    Returns
    -------
    conversion : str
        Converted (and/or scaled) ingredient string in a human-readable format.
    '''
    
    # ---- initial parsing of input string ----
    amnt_ing = amount_ingredient.split()
    
    # --- special case: eggs/yolks (no unit conversion) ---
    if "egg" in amount_ingredient or "yolk" in amount_ingredient:
        # If the ingredient is eggs/egg yolks, it assumes you just want to scale it (no volume or weight measurements)        
        num = float(amnt_ing[0]) * scaling
        ing = str(amnt_ing[1])
        conversion = f"{num} {ing}"
        
        return conversion
    
    
    # Convert to numpy array for masking
    amnt_ing = np.array(amnt_ing)
    
    # Remove trailing empty entries
    if amnt_ing[-1] == " ":
        amnt_ing = amnt_ing[:-1]
      
    # --- Separate numeric quantites from words ---
    mask = make_quant_mask(amnt_ing)
    
    # Convert quantities (including fractions like "1/2") to floats and sum
    num = sum([float(Fraction(n)) for n in amnt_ing[mask]]) * scaling 
    
    # extract non-numeric parts (measurement & name)
    words_amnt_ing = amnt_ing[~mask]
    
    # assume first word after quantity is the measurement unit
    meas = words_amnt_ing[0]
    
    
    # --- Handle simple cases (e.g. "3 peaches")
    if len(amnt_ing) == 2:               
        ing = amnt_ing[1]
        conversion = f"{num} {ing}"
        return conversion
    
    # Remove "of" if present (e.g. "cups of sugar")
    elif words_amnt_ing[1] == "of":
        words_amnt_ing = words_amnt_ing[1:]
        
    # Construct ingredient name and normalize to uppercase    
    ing = ' '.join(words_amnt_ing[1:]).upper()    
    
    # --- If ingredient is unknown or excluded, only scale (no conversion) ---
    if (ing not in df['INGREDIENT'].values) or (ing in exclude):
        num = format_num(num, valid_frac_cups)
        conversion = f"{num} {meas} {ing.lower()}"
        return conversion    
                    
# ========================
# CONVERT WEIGHT → VOLUME
# ========================
    if toCups:                          
        # Convert grams → teaspoons using KAF ingredient weight chart
        quantity = round(num/df["GRAMS_PER_TSP"][df["INGREDIENT"] == ing].values[0], 1)
        
        # if large enough (greater than 1/4 cup), express in cups
        if quantity >= 11.99:           
            quantity_cups = round(quantity/48, 2)
            num = format_num(quantity_cups, valid_frac_cups)
            
            conversion = f"{num} cups {ing.lower()}"
            
        
        else:
            # Convert total teaspoons → tablespoons + remainder
            quantity_tbsp = int(quantity // 3)
            tbsp_remainder = quantity % 1
            
            # Case 1: Remainder is a "clean" fractional tablespoon 
            if tbsp_remainder in valid_frac_tbsp:
                frac = Fraction(tbsp_remainder) 
                parts = []
        
                if quantity_tbsp:
                    parts.append(str(quantity_tbsp))
            
                if frac:
                    parts.append(str(frac))
            
                conversion = f"{' '.join(parts)} tbsp {ing.lower()}"
            
            # Case 2: Convert remainder → teaspoons
            else:
                quantity_tsp = quantity - (quantity_tbsp * 3)
                tsp_frac = Fraction(round((quantity_tsp % 1) * 8) / 8)
            
                if quantity_tbsp:
                    conversion = f"{quantity_tbsp} tbsp + {tsp_frac} tsp {ing.lower()}"
                else:
                    conversion = f"{tsp_frac} tsp {ing.lower()}"
            
        return conversion

# ========================
# CONVERT VOLUME → WEIGHT
# ======================== 
    else:
        # Select appropriate conversion factor based on unit
               
        if meas == "cup" or meas == "cups": 
            quantity = num*df["GRAMS_PER_CUP"][df["INGREDIENT"] == ing].values[0]       
            
        elif meas == "tbsp" or meas=='tbsps': 
            quantity = num*df["GRAMS_PER_TBSP"][df["INGREDIENT"] == ing].values[0]      
            
        elif meas == "tsp" or meas=='tsps':
            quantity = num*df["GRAMS_PER_TSP"][df["INGREDIENT"] == ing].values[0]      
            
        elif meas == "fl oz" or meas=='fluid ounces':
            quantity = num/8 * df["GRAMS_PER_CUP"][df["INGREDIENT"] == ing].values[0]       
    
        else:
            print('Unvalid measure type. Must be cups, tablespoons, teaspoons, ounces, fluid ounces')
            
        # format final output (rounded to 0.1 g)
        conversion = f"{str(round(quantity, 1))} g {ing.lower()}" 
        
        
        return conversion
            


def convert_recipe_lines(lines, toCups=False, exclude=None, scaling=1):
    """
    Convert a list of recipe lines while preserving section structure.

    Parameters
    ----------
    lines : list of str
        Recipe lines (including headers and ingredients).

    toCups : bool, optional
        Conversion direction (see `convert_ingredient`).

    exclude : list of str, optional
        Ingredients to exclude from conversion.

    scaling : float, optional
        Scaling factor for ingredient quantities.

    Returns
    -------
    converted_lines : list of str
        Converted recipe with original structure preserved.
    """
    if exclude is None:
        exclude = []

    exclude = [x.upper() for x in exclude]

    converted_lines = []

    for line in lines:
        stripped = line.strip()

        # Preserve empty lines
        if not stripped:
            converted_lines.append("")
            continue

        # Preserve section headers
        if is_section_header(line):
            converted_lines.append(line)
            continue

        # Convert ingredient lines
        try:
            conv = convert_ingredient(line, exclude, toCups, scaling)
            converted_lines.append(conv)
        except Exception:
            # Fallback: keep original line if conversion fails
            converted_lines.append(line)

    return converted_lines


def convert_recipe(recipe_file, toCups=False, exclude=None, scaling=1):
    """
    Read a recipe file, convert its ingredient lines, and return the result.

    This is a thin wrapper around `convert_recipe_lines` that handles file I/O.

    Parameters
    ----------
    recipe_file : str
        Path to recipe text file.

    toCups : bool, optional
        Conversion direction.

    exclude : list of str, optional
        Ingredients to exclude from conversion.

    scaling : float, optional
        Scaling factor.

    Returns
    -------
    converted_recipe : list of str
        Converted recipe lines.
    """
    with open(recipe_file, "r") as f:
        lines = f.read().splitlines()

    return convert_recipe_lines(lines, toCups, exclude, scaling)

