
import os

def get_offer_files(directory="ofertas"):
    """
    Scans the 'ofertas' directory and returns a list of absolute paths
    to valid offer files (PDFs, Images).
    """
    valid_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
    files_to_send = []
    
    if not os.path.exists(directory):
        return []

    for filename in os.listdir(directory):
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_extensions:
            files_to_send.append(os.path.join(os.getcwd(), directory, filename))
            
    return files_to_send
