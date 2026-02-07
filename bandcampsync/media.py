from unicodedata import normalize
from .logger import get_logger


log = get_logger("media")


class LocalMedia:
    """
    A local media directory indexer. This stores media in the following format:

        /media_dir/
        /media_dir/Artist Name
        /media_dir/Artist Name/Album Name
        /media_dir/Artist Name/Album Name/bandcamp_item_id.txt
        /media_dir/Artist Name/Album Name/track1.flac
        /media_dir/Artist Name/Album Name/track2.flac
    """

    ITEM_INDEX_FILENAME = "bandcamp_item_id.txt"

    def __init__(self, media_dir, library_dir=None):
        self.media_dir = media_dir
        self.library_dir = library_dir
        self.media = {}
        self.item_names = set()
        self.library_albums = set()
        log.info(f"Local media directory: {self.media_dir}")
        self._index_directory(self.media_dir)
        if self.library_dir:
            log.info(f"Library directory: {self.library_dir}")
            self._index_library(self.library_dir)

    def _clean_path(self, path_str):
        path_str = str(path_str)
        disallowed_punctuation = "\"#%'*/?\\`:"
        normalized_path = normalize("NFKD", path_str)
        outstr = ""
        for c in normalized_path:
            if c not in disallowed_punctuation:
                outstr += c
        return outstr

    def clean_format(self, format_str):
        if "-" not in format_str:
            return format_str
        format_parts = format_str.split("-")
        format_prefix = format_parts[0]
        return format_prefix if format_prefix else format_str

    def _index_directory(self, directory):
        if not directory.is_dir():
            return
        for child1 in directory.iterdir():
            if child1.is_dir():
                for child2 in child1.iterdir():
                    if child2.is_dir():
                        for child3 in child2.iterdir():
                            if child3.name == self.ITEM_INDEX_FILENAME:
                                item_id = self.read_item_id(child3)
                                self.media[item_id] = child2
                                self.item_names.add((child2.parent.name, child2.name))
                                log.info(
                                    f"Detected locally downloaded media: {item_id} = {child2}"
                                )

    def _index_library(self, directory):
        if not directory.is_dir():
            return
        for artist_dir in directory.iterdir():
            if artist_dir.is_dir():
                for album_dir in artist_dir.iterdir():
                    if album_dir.is_dir():
                        self.library_albums.add(
                            (artist_dir.name.lower(), album_dir.name.lower())
                        )
        log.info(f"Indexed {len(self.library_albums)} albums from library directory")

    def read_item_id(self, filepath):
        with open(filepath, "rt") as f:
            item_id = f.read().strip()
        try:
            return int(item_id)
        except Exception as e:
            raise ValueError(
                f'Failed to cast item ID from {filepath} "{item_id}" as an int: {e}'
            ) from e

    def is_locally_downloaded(self, item, local_path):
        if item.item_id in self.media:
            return True
        item_name = (local_path.parent.name, local_path.name)
        if item_name in self.item_names:
            log.info(
                f'Detected album at "{local_path}" but with an item ID mismatch '
                f"({self.ITEM_INDEX_FILENAME} file does not contain {item.item_id}), "
                f"you may want to check this item is correctly downloaded"
            )
            return True
        if self.library_albums:
            library_key = (item.band_name.strip().lower(), item.item_title.strip().lower())
            if library_key in self.library_albums:
                log.info(
                    f'Found in library, skipping: "{item.band_name} / {item.item_title}" '
                    f"(id:{item.item_id})"
                )
                return True
        return False

    def get_path_for_purchase(self, item):
        return (
            self.media_dir
            / self._clean_path(item.band_name)
            / self._clean_path(item.item_title)
        )

    def get_path_for_file(self, local_path, file_name):
        return local_path / self._clean_path(file_name)

    def write_bandcamp_id(self, item, dirpath):
        outfile = dirpath / self.ITEM_INDEX_FILENAME
        log.info(f"Writing bandcamp item id:{item.item_id} to: {outfile}")
        with open(outfile, "wt") as f:
            f.write(f"{item.item_id}\n")
        return True
