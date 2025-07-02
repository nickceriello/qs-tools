import sys
import argparse
from collections import defaultdict

# ... (the definitions for SPECIFIC_SYMBOLS and HTML_SENSITIVE_CHARS remain the same) ...
SPECIFIC_SYMBOLS = {"•", "–", "—", "™", "©", "®"}
HTML_SENSITIVE_CHARS = {'<', '>', '&', '"', "'"}

def analyze_file(file_path, file_encoding):
    """
    Analyzes a file for characters that would be modified by the PHP function.
    
    Args:
        file_path (str): The path to the text file to analyze.
        file_encoding (str): The encoding of the file (e.g., 'utf-8', 'windows-1252').
    """
    matches = defaultdict(lambda: defaultdict(list))
    
    print(f"Attempting to read file with '{file_encoding}' encoding...")
    
    try:
        # Use the specified encoding
        with open(file_path, 'r', encoding=file_encoding) as f:
            for line_num, line in enumerate(f, 1):
                for col_num, char in enumerate(line, 1):
                    if char in SPECIFIC_SYMBOLS:
                        matches["Specific Symbols"][char].append((line_num, col_num))
                    elif char in HTML_SENSITIVE_CHARS:
                        matches["HTML Sensitive Characters"][char].append((line_num, col_num))
                    # The check for ord(char) >= 128 works for any single-byte encoding too
                    elif ord(char) >= 128:
                        matches["Accented/Non-ASCII"][char].append((line_num, col_num))

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"\n--- DECODING FAILED ---")
        print(f"Error: The file '{file_path}' could not be decoded using '{file_encoding}'.")
        print("The file is likely saved with a different encoding.")
        print("Try another common encoding, such as 'windows-1252' or 'latin-1'.")
        print("Example: python find_special_chars.py --encoding windows-1252 your_file.txt")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
        
    return matches

# ... (The print_results function remains the same) ...
def print_results(matches, file_path):
    """Prints the analysis results in a readable format."""
    print(f"\n🔍 Analysis results for: {file_path}\n")
    
    if not matches:
        print("✅ No special characters found that would be altered by the PHP function.")
        return

    for category, chars in matches.items():
        print(f"--- {category} ---")
        for char, locations in chars.items():
            loc_str = ", ".join([f"L{l:03d}:C{c:03d}" for l, c in locations[:5]])
            if len(locations) > 5:
                loc_str += f" ...and {len(locations) - 5} more"
            
            print(f"  Character: '{char}' found {len(locations)} time(s)")
            print(f"  Locations: [{loc_str}]")
        print()

def main():
    """Main function to parse arguments and run the analysis."""
    parser = argparse.ArgumentParser(
        description="Search a file for special characters based on a specific PHP normalization function."
    )
    parser.add_argument(
        "filename", 
        help="The path to the text file you want to analyze."
    )
    # Add an optional argument for encoding
    parser.add_argument(
        "-e", "--encoding",
        default="utf-8",
        help="The text encoding of the file. Defaults to 'utf-8'. Try 'windows-1252' if you get errors."
    )
    args = parser.parse_args()
    
    found_matches = analyze_file(args.filename, args.encoding)
    print_results(found_matches, args.filename)

if __name__ == "__main__":
    main()