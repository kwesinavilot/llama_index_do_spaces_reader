from typing import Callable, Dict, List, Optional, Union, BinaryIO, Any
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.readers.base import BaseReader, BasePydanticReader
from llama_index.core.schema import Document
from llama_index.core.bridge.pydantic import Field
from s3fs import S3FileSystem

class DOSpacesReader(BasePydanticReader):
    """
    General reader for any DigitalOcean Spaces file or directory.

    If key is not set, the entire bucket (filtered by prefix) is parsed.

    Args:
        bucket (str): the name of your DigitalOcean Spaces bucket
        key (Optional[str]): the name of the specific file. If none is provided,
            this loader will iterate through the entire bucket.
        prefix (Optional[str]): the prefix to filter by in the case that the loader
            iterates through the entire bucket. Defaults to empty string.
        recursive (bool): Whether to recursively search in subdirectories.
            True by default.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that file
            to text. See `SimpleDirectoryReader` for more details.
        required_exts (Optional[List[str]]): List of required extensions.
            Default is None.
        num_files_limit (Optional[int]): Maximum number of files to read.
            Default is None.
        file_metadata (Optional[Callable[str, Dict]]): A function that takes
            in a filename and returns a Dict of metadata for the Document.
            Default is None.
        do_spaces_key_id (str): DigitalOcean Spaces key ID.
        do_spaces_secret_key (str): DigitalOcean Spaces secret key.
        do_spaces_endpoint_url (str): DigitalOcean Spaces endpoint URL.
    """

    is_remote: bool = True

    bucket: str
    key: Optional[str] = None
    prefix: Optional[str] = ""
    recursive: bool = True
    file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = Field(
        default=None, exclude=True
    )
    required_exts: Optional[List[str]] = None
    filename_as_id: bool = True
    num_files_limit: Optional[int] = None
    file_metadata: Optional[Callable[[str], Dict]] = Field(default=None, exclude=True)
    do_spaces_key_id: str
    do_spaces_secret_key: str
    do_spaces_endpoint_url: str

    @classmethod
    def class_name(cls) -> str:
        return "DOSpacesReader"

    def _setup_s3fs(self) -> S3FileSystem:
        """
        Set up the S3FileSystem instance for DigitalOcean Spaces.

        Returns:
            S3FileSystem: An instance of S3FileSystem configured for DigitalOcean Spaces.
        """
        return S3FileSystem(
            key=self.do_spaces_key_id,
            endpoint_url=self.do_spaces_endpoint_url,
            secret=self.do_spaces_secret_key,
        )

    def exists(self, path: str) -> bool:
        """
        Check if a file or directory exists in the DigitalOcean Space.

        Args:
            path (str): The path to the file or directory in the DigitalOcean Space.

        Returns:
            bool: True if the file or directory exists, False otherwise.
        """
        s3fs = self._setup_s3fs()
        return s3fs.exists(f"{self.bucket}/{path}")

    def makedirs(self, path: str, exist_ok: bool = False) -> None:
        """
        Recursively make directories on DigitalOcean Spaces.

        Args:
            path (str): The path to create directories.
            exist_ok (bool, optional): If True, ignore existing directory. Defaults to False.
        """
        s3fs = self._setup_s3fs()
        s3fs.makedirs(f"{self.bucket}/{path}", exist_ok=exist_ok)

    def open(
        self,
        path: str,
        mode: str = "r",
        block_size: Optional[int] = None,
        cache_options: Optional[Dict] = None,
        **kwargs: Any,
    ) -> BinaryIO:
        """
        Open a file on DigitalOcean Spaces.

        Args:
            path (str): The path to the file.
            mode (str, optional): The mode to open the file. Defaults to "r".
            block_size (int, optional): The block size to use for buffering. Defaults to None.
            cache_options (Dict, optional): Options to control caching behavior. Defaults to None.
            **kwargs (Any): Additional keyword arguments to pass to S3FileSystem.open.

        Returns:
            BinaryIO: A file-like object for the opened file.
        """
        s3fs = self._setup_s3fs()
        return s3fs.open(
            f"{self.bucket}/{path}",
            mode=mode,
            block_size=block_size,
            cache_options=cache_options,
            **kwargs,
        )

    def load_do_spaces_files_as_docs(self) -> List[Document]:
        """Load file(s) from DigitalOcean Spaces."""
        s3fs = self._setup_s3fs()

        input_dir = self.bucket
        input_files = None

        if self.key:
            input_files = [f"{self.bucket}/{self.key}"]
        elif self.prefix:
            input_dir = f"{input_dir}/{self.prefix}"

        loader = SimpleDirectoryReader(
            input_dir=input_dir,
            input_files=input_files,
            file_extractor=self.file_extractor,
            required_exts=self.required_exts,
            filename_as_id=self.filename_as_id,
            num_files_limit=self.num_files_limit,
            file_metadata=self.file_metadata,
            recursive=self.recursive,
            fs=s3fs,
        )

        return loader.load_data()

    def load_data(self) -> List[Document]:
        """
        Load the file(s) from DigitalOcean Spaces.

        Returns:
            List[Document]: A list of documents loaded from DigitalOcean Spaces.
        """
        documents = self.load_do_spaces_files_as_docs()
        for doc in documents:
            doc.id_ = "do_spaces_" + doc.id_

        return documents
    
    # function to get the created s3 instance

    @property
    def s3(self) -> S3FileSystem:
        return self._setup_s3fs()
    
    def listdir(self, path: str) -> List[str]:
        """
        List all files and directories within the given path.

        Args:
            path (str): The path to list files and directories.

        Returns:
            List[str]: A list of file and directory names within the given path.
        """
        return [obj.split("/")[-1] for obj in self.ls(path, detail=False)]