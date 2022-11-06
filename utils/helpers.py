from os import listdir, path, remove
from pathlib import Path


def join_file_parts(
        directory, file_to_write=None, file_prefix=None, buffer_size=1024, echo=None
) -> None:
    """
    Joins files placed in dir to one big file

    :param directory: Directory where file parts placed
    :type directory: str
    :param file_to_write: File or directory where to save joined parts
    :type file_to_write: str
    :param file_prefix: Beginning of the file parts (useful when not only requested file parts placed in directory)
    :type file_prefix: str
    :param buffer_size: Size of buffer read adn writes data (in bytes)
    :type buffer_size; int
    :param echo: Print messages or not
    :type echo: bool
    """

    if file_prefix is None:
        files_to_write = listdir(directory)
    else:
        files_to_write = list(
            filter(
                lambda filename: filename.startswith(file_prefix), listdir(directory)
            )
        )
    files_to_write.sort(key=lambda filename: Path(filename).suffix)

    if not files_to_write:
        if echo:
            print("Empty directory or wrong file_prefix, nothing to do")
        return

    if not file_to_write:
        out_file_path = path.join(directory, Path(files_to_write[0]).stem)
    elif path.isdir(file_to_write):
        out_file_path = path.join(file_to_write, Path(files_to_write[0]).stem)
    else:
        out_file_path = file_to_write

    if echo:
        [print(path.join(directory, file)) for file in files_to_write]
        print(f"-> {out_file_path}")

    if path.isfile(out_file_path):
        remove(out_file_path)
        if echo:
            print(f"Old {out_file_path} deleted")

    with open(out_file_path, "wb") as out_file:
        for in_file_path in files_to_write:
            with open(path.join(directory, in_file_path), "rb") as in_file:
                while data := in_file.read(buffer_size):
                    out_file.write(data)
    if echo:
        print("Success")
