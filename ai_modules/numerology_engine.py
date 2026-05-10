def calculate_life_path_number(dob: str) -> int:
    """
    Calculates the life path number from a Date of Birth string.
    Supports YYYY-MM-DD or DD/MM/YYYY.
    """
    if not dob:
        return 1  # Fallback
        
    # Extract only digits from the DOB string to handle any separator
    digits = [int(char) for char in dob if char.isdigit()]
    
    if not digits:
        return 1 # Fallback
    
    # Sum all the digits
    total = sum(digits)
    
    # Reduce to a single digit
    while total > 9:
        total = sum(int(char) for char in str(total))
        
    return total
