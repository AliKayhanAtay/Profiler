import os
from tqdm.auto import tqdm

def get_files(root_dir):
    file_paths = []
    for current_root, dirs, files in tqdm(os.walk(root_dir)):
        for name in files:
            full_path = os.path.join(current_root, name)
            file_paths.append(full_path)
    return file_paths
