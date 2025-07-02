from flask import Flask, render_template, request, redirect, url_for, flash
import os
from collections import defaultdict
from werkzeug.utils import secure_filename

# Import the analysis logic from legacy.py
SPECIFIC_SYMBOLS = {"•", "–", "—", "™", "©", "®"}
HTML_SENSITIVE_CHARS = {'<', '>', '&', '"', "'"}

# Common encodings to try automatically
COMMON_ENCODINGS = ['utf-8', 'windows-1252', 'latin-1', 'iso-8859-1', 'ascii']

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'txt', 'csv'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_file(file_path, file_encoding=None):
    """
    Analyzes a file for characters that would be modified by the PHP function.
    If file_encoding is None, tries multiple common encodings automatically.
    
    Args:
        file_path (str): The path to the text file to analyze.
        file_encoding (str, optional): The encoding of the file. If None, tries multiple encodings.
    
    Returns:
        tuple: (matches, successful_encoding, error_message)
    """
    if file_encoding is not None:
        # If encoding is specified, use only that one
        encodings_to_try = [file_encoding]
    else:
        # Otherwise try common encodings in order
        encodings_to_try = COMMON_ENCODINGS
    
    last_error = None
    for encoding in encodings_to_try:
        matches = defaultdict(lambda: defaultdict(list))
        
        try:
            # Try with current encoding
            with open(file_path, 'r', encoding=encoding) as f:
                for line_num, line in enumerate(f, 1):
                    for col_num, char in enumerate(line, 1):
                        if char in SPECIFIC_SYMBOLS:
                            matches["Specific Symbols"][char].append((line_num, col_num))
                        elif char in HTML_SENSITIVE_CHARS:
                            matches["HTML Sensitive Characters"][char].append((line_num, col_num))
                        # The check for ord(char) >= 128 works for any single-byte encoding too
                        elif ord(char) >= 128:
                            matches["Accented/Non-ASCII"][char].append((line_num, col_num))
            # If we get here, the encoding worked
            return matches, encoding, None
        except UnicodeDecodeError:
            last_error = f"Could not decode with '{encoding}'"
            continue
        except Exception as e:
            return None, None, f"An unexpected error occurred: {e}"
    
    # If we get here, all encodings failed
    return None, None, f"Failed to decode the file with any of the common encodings: {', '.join(encodings_to_try)}. {last_error}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser submits an empty file without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Analyze the file with automatic encoding detection
            results, detected_encoding, error = analyze_file(filepath)
            
            if error:
                flash(error)
                return redirect(request.url)
            
            # Process results for display
            processed_results = {}
            for category, chars in results.items():
                processed_results[category] = []
                for char, locations in chars.items():
                    loc_str = ", ".join([f"L{l:03d}:C{c:03d}" for l, c in locations[:5]])
                    if len(locations) > 5:
                        loc_str += f" ...and {len(locations) - 5} more"
                    
                    processed_results[category].append({
                        'character': char,
                        'count': len(locations),
                        'locations': loc_str
                    })
            
            return render_template('results.html', 
                                  filename=filename, 
                                  results=processed_results,
                                  has_results=bool(processed_results),
                                  encoding=detected_encoding)
        else:
            flash('File type not allowed. Please upload a .txt or .csv file.')
            return redirect(request.url)
    
    return render_template('index.html')

@app.route('/try_encoding', methods=['POST'])
def try_encoding():
    filename = request.form.get('filename')
    encoding = request.form.get('encoding')
    
    if not filename or not encoding:
        flash('Missing filename or encoding')
        return redirect(url_for('index'))
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if not os.path.exists(filepath):
        flash('File not found')
        return redirect(url_for('index'))
    
    # Analyze with specific encoding
    results, detected_encoding, error = analyze_file(filepath, encoding)
    
    if error:
        flash(error)
        return redirect(url_for('index'))
    
    # Process results for display
    processed_results = {}
    for category, chars in results.items():
        processed_results[category] = []
        for char, locations in chars.items():
            loc_str = ", ".join([f"L{l:03d}:C{c:03d}" for l, c in locations[:5]])
            if len(locations) > 5:
                loc_str += f" ...and {len(locations) - 5} more"
            
            processed_results[category].append({
                'character': char,
                'count': len(locations),
                'locations': loc_str
            })
    
    return render_template('results.html', 
                          filename=filename, 
                          results=processed_results,
                          has_results=bool(processed_results),
                          encoding=detected_encoding)

if __name__ == '__main__':
    app.run(debug=True)
