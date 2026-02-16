import os
import shutil

def clear_data_folders():
    folders = [
        "data/pdfs",
        "data/texts",
        "data/dist_texts",
        "data/metadata",
        "data/output"
    ]

    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
