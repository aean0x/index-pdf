import fitz
import concurrent.futures
import hashlib
import pickle
import os

INDEX_FILE = "pdf_index.pkl"

def hash_file(file_path):
    """Generate a hash for the given file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def index_pdf(file_path):
    """Index the text of a PDF file."""
    doc = fitz.open(file_path)
    index = []
    
    def process_page(page_num):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.splitlines()
        return [(page_num + 1, line_num + 1, line) for line_num, line in enumerate(lines)]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_page, range(doc.page_count)))
    
    for result in results:
        index.extend(result)
    
    return index

def save_index(index, hash_value):
    """Save the index to a file."""
    with open(INDEX_FILE, 'wb') as f:
        pickle.dump((hash_value, index), f)

def load_index():
    """Load the index from a file."""
    if not os.path.exists(INDEX_FILE):
        return None, None
    with open(INDEX_FILE, 'rb') as f:
        return pickle.load(f)

def search_index(index, search_term):
    """Search for the term in the index."""
    matches = []
    for page_num, line_num, line in index:
        if search_term in line:
            matches.append((page_num, line_num, line))
    return matches

def main():
    file_path = input("Enter PDF file path: ")
    hash_value = hash_file(file_path)
    saved_hash, index = load_index()
    
    if saved_hash == hash_value and index is not None:
        print("Using saved index...")
    else:
        print("Indexing PDF...")
        index = index_pdf(file_path)
        save_index(index, hash_value)
    
    while True:
        search_term = input("Enter search term: ")
        matches = search_index(index, search_term)
        if matches:
            for page_num, line_num, line in matches:
                print(f"Page {page_num}, Line {line_num}: {line}")
        else:
            print("No matches found.")

if __name__ == "__main__":
    main()
