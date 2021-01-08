import os
from os import listdir
from os.path import isfile, join
import shelve

def write_text_file(project_folder_path, text, file_name):
    """Create a Textfile for the given text.

    Args:
      project_folder_path: Folder in which the text-file should be saved.
      text: The Text.
      file_name: The file-name of the text-file.

    """

    file_path = os.path.join(project_folder_path, file_name + ".txt")
    with open(file_path, "w") as f:
        f.write(text)

def save_to_shelve(project_folder_path, key, value, shelve_name = "persistent"):
    """Saves the given key and value to a shelve.

    Args:
      project_folder_path: The project-folder where the shelve is saved.
      key: The key.
      value: The value.
      shelve_name: The name of the shelve, where the key , value pair should be saved. (Default value = "persistent")

    """

    with shelve.open(os.path.join(project_folder_path, shelve_name)) as sh:
        sh[key] = value

def get_value_from_shelve(project_folder_path, key, default = None, shelve_name = "persistent",):
    """Returns a value for a given key from a shelve.

    Args:
      project_folder_path: The project-folder where the shelve is saved.
      key: The key.
      default: Default value if the key is not in the shelve. (Default value = None)
      shelve_name: In which shelve the key should be searched. (Default value = "persistent")

    Returns:
      The value for the given key or the given default.
    """

    with shelve.open(os.path.join(project_folder_path, shelve_name)) as sh:
        return sh.get(key, default)

def get_all_values_from_shelve(project_folder_path, shelve_name = "persistent"):
    """Returns all values from a shelve.

    Args:
      project_folder_path: The folder-path where the shelve is saved.
      shelve_name: The shelve-name. (Default value = "persistent")

    Returns:
      All key value pairs in the shelves as a dict.
    """

    with shelve.open(os.path.join(project_folder_path, shelve_name)) as sh:
        keys = sh.keys()
        dict = {}

        for key in keys:
            dict[key] = sh.get(key)

        return dict

def get_file(folder_path, filter):
    """Finds a file with given filter.

    Args:
      folder_path: The folder which should be searched.
      filter: The part which needs to be in the file name.

    Returns:
      The path of the found file or none if more than one or none is found.
    """

    files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]

    files = [s for s in files if filter in s]

    if len(files) != 1:
        return None

    return os.path.join(folder_path, files[0])