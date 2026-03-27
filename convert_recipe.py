import numpy as np
import pandas as pd
from fractions import Fraction

df = pd.read_csv("king_arthur_ingredient_weights2.csv")

def make_quant_mask(lst):
    '''

    Parameters
    ----------
    lst : list (strings)
        Checks which strings are Fractions/floats/integers

    Returns
    -------
    array (bool)
        Mask specifying location of Fractions/floats/integers.

    '''
    frac_mask = []
    for s in lst:
        if s.isnumeric():
            frac_mask.append(True)
            
        else:
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

    Args:
        num (float): The number to format.

    Returns:
        str: A string representation of the number as a mixed fraction if valid,
             otherwise the original number as a string.

    Examples:
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
            return Fraction(decimal)
        else:
            return f"{whole} {Fraction(decimal)}"
    else:
        return str(num)

valid_frac_cups = [0.0, 0.25, 0.5, 0.75, 0.33, 0.66]
valid_frac_tbsp = np.arange(0, 1, 1/8)



def convert_ingredient(amount_ingredient, exclude, toCups, scaling = 1):
    '''
    Converts ingredient line into weight/volume measurement 
    
    
   Parameters
   ----------
   amount_ingredient : string
        String with ingredient quantity, measurement, and ingredient name
        "1.5 cups sugar", "1 1/2 cups sugar", "1.5 cups of sugar", "1 1/2 cups of sugar" all accepted
        
    exlude : list [strings]
        List of ingredients to not convert, strings should be all capitalized
        
    toCups : bool
        True if you want the conversion from weight -> volume measurement
        
    scaling : float
        If you want to change the amount of the recipe (must be positive)
   
   Returns
   -------
   conversion : string
        String with converted ingredient amount
        
        
    '''
    amnt_ing = amount_ingredient.split()
    
    if "egg" in amount_ingredient or "yolk" in amount_ingredient:
        # If the ingredient is eggs/egg yolks, it assumes you just want to scale it (no volume or weight measurements)        
        num = float(amnt_ing[0]) * scaling
        ing = str(amnt_ing[1])
        conversion = f"{num} {ing}"
        
        return conversion
    
    
    # ---- break into quantity, measurement, ingredient ----
    amnt_ing = np.array(amnt_ing)
    
    if amnt_ing[-1] == " ":
        amnt_ing = amnt_ing[:-1]        # remove empty space at the end of lines
      
    # make a mask to separate quantities (floats, ints, fractions) from words
    mask = make_quant_mask(amnt_ing)
    # total measured quantity (2 1/4 = 2.25)
    num = sum([float(Fraction(n)) for n in amnt_ing[mask]]) * scaling 
    # non-quanitity values
    words_amnt_ing = amnt_ing[~mask]
    meas = words_amnt_ing[0]            # assuming that measurement (cups/tbsp/tsp/oz/g) follows after measurement


    # -- define ingredient name --
    if len(amnt_ing) == 2:              # if the ingredient line is two words (3 peaches) -- scale it 
        ing = amnt_ing[1]
        conversion = f"{num} {ing}"
        return conversion

    elif words_amnt_ing[1] == "of":     # if "of" is in the statement (1.5 cups of sugar) -- exclude from the line
        words_amnt_ing = words_amnt_ing[1:]
    
    ing = ' '.join(words_amnt_ing[1:]).upper()    
    
    if (ing not in df['INGREDIENT'].values) or (ing in exclude):    # if ingredient not in king arthur flour csv or excluded
        num = format_num(num, valid_frac_cups)
        conversion = f"{num} {meas} {ing.lower()}"
        return conversion    
                    

    if toCups:                          # if converting from weight -> volume
        # convert to tsp first
        quantity = round(num/df["GRAMS_PER_TSP"][df["INGREDIENT"] == ing].values[0], 1)
        
        if quantity >= 11.99:           # if the amount is greater than 1/4 cup
            quantity_cups = round(quantity/48, 2)
            num = format_num(quantity_cups, valid_frac_cups)
            
            conversion = f"{num} cups {ing.lower()}"
            
        
        else:
            # Convert total quantity (in teaspoons) into whole tablespoons
            quantity_tbsp = int(quantity // 3)
            
            # Get the fractional remainder after removing whole tablespoons
            tbsp_remainder = quantity % 1
            
            # Case 1: Fractional tablespoon is valid (e.g., 1/4, 1/2, etc.)
            if tbsp_remainder in valid_frac_tbsp:
                frac = Fraction(tbsp_remainder)  # Convert remainder to exact fraction
                parts = []
            
                # Add whole tablespoon part if it exists
                if quantity_tbsp:
                    parts.append(str(quantity_tbsp))
            
                # Add fractional part if it exists (non-zero)
                if frac:
                    parts.append(str(frac))
            
                # Join parts into a mixed number string (e.g., "1 1/2 tbsp sugar")
                conversion = f"{' '.join(parts)} tbsp {ing.lower()}"
            
            # Case 2: Fractional tablespoon is NOT valid → convert remainder to teaspoons
            else:
                # Remaining teaspoons after removing whole tablespoons
                quantity_tsp = quantity - (quantity_tbsp * 3)
            
                # Convert fractional tsp to nearest 1/8 for cleaner measurement
                tsp_frac = Fraction(round((quantity_tsp % 1) * 8) / 8)
            
                # If no whole tablespoons, just show teaspoons
                if quantity_tbsp:
                    conversion = f"{quantity_tbsp} tbsp + {tsp_frac} tsp {ing.lower()}"
                else:
                    conversion = f"{tsp_frac} tsp {ing.lower()}"
            
        return conversion
    
    else:               # want to convert from cups -> weight
        if meas == "cup" or meas == "cups": 
            quantity = num*df["GRAMS_PER_CUP"][df["INGREDIENT"] == ing].values[0]           # multiply scaled num by the grams/cups
        elif meas == "tbsp" or meas=='tbsps': 
            quantity = num*df["GRAMS_PER_TBSP"][df["INGREDIENT"] == ing].values[0]          # multiple scaled num by grams/tbsp
        elif meas == "tsp" or meas=='tsps':
            quantity = num*df["GRAMS_PER_TSP"][df["INGREDIENT"] == ing].values[0]           # multiply scaled num by grams/tsp
        elif meas == "fl oz" or meas=='fluid ounces':
            quantity = num/8 * df["GRAMS_PER_CUP"][df["INGREDIENT"] == ing].values[0]       # multiply fluid ounce by grams/oz
    
        else:
            print('Unvalid measure type. Must be cups, tablespoons, teaspoons, ounces, fluid ounces')
    
        conversion = f"{str(round(quantity, 1))} g {ing.lower()}" 
        
        
        return conversion
            
            
def convert_recipe(recipe_file, toCups = False, exclude = [], scaling = 1):
    exclude = [x.upper() for x in exclude]
    recipe = open(recipe_file, "r").read().splitlines()
    
    for i in range(len(recipe)):
        conv = convert_ingredient(recipe[i], exclude, toCups, scaling)
        print(conv)