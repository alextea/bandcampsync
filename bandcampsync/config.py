import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


VERSION = "0.7.0"
INTERNAL_USER_AGENT = f"bandcampsync/{VERSION}"

DEFAULT_CONFIG_PATH = Path("/config/config.toml")


class Config:

    DEFAULTS = {
        "cookies_file": "/config/cookies.txt",
        "directory": "/downloads",
        "library_directory": "",
        "format": "flac",
        "temp_directory": "",
        "concurrency": 1,
        "max_retries": 3,
        "retry_wait": 5,
        "notify_url": "",
        "ignores": {
            "file": "",
            "patterns": "",
        },
    }

    def __init__(
        self,
        cookies_file="/config/cookies.txt",
        directory="/downloads",
        library_directory="",
        media_format="flac",
        temp_directory="",
        concurrency=1,
        max_retries=3,
        retry_wait=5,
        notify_url="",
        ignore_file="",
        ignore_patterns="",
    ):
        self.cookies_file = cookies_file
        self.directory = directory
        self.library_directory = library_directory
        self.format = media_format
        self.temp_directory = temp_directory
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.retry_wait = retry_wait
        self.notify_url = notify_url
        self.ignore_file = ignore_file
        self.ignore_patterns = ignore_patterns

    @classmethod
    def from_file(cls, path):
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)
        section = data.get("bandcampsync", {})
        ignores = section.get("ignores", {})
        return cls(
            cookies_file=section.get("cookies_file", cls.DEFAULTS["cookies_file"]),
            directory=section.get("directory", cls.DEFAULTS["directory"]),
            library_directory=section.get("library_directory", cls.DEFAULTS["library_directory"]),
            media_format=section.get("format", cls.DEFAULTS["format"]),
            temp_directory=section.get("temp_directory", cls.DEFAULTS["temp_directory"]),
            concurrency=section.get("concurrency", cls.DEFAULTS["concurrency"]),
            max_retries=section.get("max_retries", cls.DEFAULTS["max_retries"]),
            retry_wait=section.get("retry_wait", cls.DEFAULTS["retry_wait"]),
            notify_url=section.get("notify_url", cls.DEFAULTS["notify_url"]),
            ignore_file=ignores.get("file", cls.DEFAULTS["ignores"]["file"]),
            ignore_patterns=ignores.get("patterns", cls.DEFAULTS["ignores"]["patterns"]),
        )
