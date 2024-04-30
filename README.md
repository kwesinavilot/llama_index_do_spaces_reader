# DOSpacesReader

`DOSpacesReader` is a custom reader for the LlamaIndex, designed to enable efficient loading and indexing of documents directly from DigitalOcean Spaces buckets. This reader streamlines the process of ingesting and managing indexes stored in DigitalOcean Spaces, making it easier to build and maintain knowledge bases or search engines powered by LlamaIndex.

By integrating `DOSpacesReader` into their LlamaIndex workflows, developers can leverage the scalability and durability of DigitalOcean Spaces for storing and retrieving large volumes of data and indexes, while benefiting from the powerful indexing and querying capabilities of LlamaIndex.

## Features
- Persist and load LlamaIndex vector stores directly to and from DigitalOcean Spaces
- Support for recursive directory traversal
- Filter files by extension
- Set a maximum number of files to read
- Customize file metadata extraction

## Prerequisites
- Python 3.6 or higher
- `llama_index` library installed (`pip install llama_index`)
- `s3fs` library installed (`pip install s3fs`)
- DigitalOcean Spaces credentials (access key, secret key, and endpoint URL)

## Parameters

The reader class expects the following DigitalOcean Spaces credentials:

- `bucket`: The name of your DigitalOcean Spaces bucket
- `prefix`: The prefix of the files to read from the DigitalOcean Spaces bucket
- `do_spaces_key_id`: Your DigitalOcean Spaces Access Key ID
- `do_spaces_secret_key`: Your DigitalOcean Spaces Secret Access Key
- `do_spaces_endpoint_url`: The origin URL of your DigitalOcean Spaces bucket

You can also just pass in the keys directly when creating the DOSpacesReader instance

## Usage Example
```python
import os
from llama_index import VectorStoreIndex, StorageContext, load_index_from_storage
from DOSpacesReader import DOSpacesReader

# Create a DOSpacesReader instance, from environment variables in this case
reader = DOSpacesReader(
    bucket="your_bucket_name",
    prefix="documents/",
    do_spaces_key_id=os.getenv('DO_SPACES_KEY_ID'),
    do_spaces_secret_key=os.getenv('DO_SPACES_SECRET_KEY'),
    do_spaces_endpoint_url=os.getenv('DO_SPACES_ORIGIN_URL'),
)

# check if we have a persisted index already. if not, create one
if not PERSIST_DIR:
    # Load documents from DigitalOcean Spaces
    documents = reader.load_data()

    # Create a fresh vector store index on the documents
    index = VectorStoreIndex.from_documents(documents)

    # Persist the index to a directory in DigitalOcean Spaces
    index.storage_context.persist(persist_dir='path/to/persist/dir', fs=reader)
else: 
    # if we have a persisted index, load it from a directory in DigitalOcean Spaces

    # first, create a storage context by loading the index from a directory in DigitalOcean Spaces
    storage_context = StorageContext.from_defaults(persist_dir='path/to/persist/dir', fs=reader)
    
    # then, load the index from the storage context
    index = load_index_from_storage(storage_context)

# create a query engine from the index
query_engine = index.as_query_engine(similarity_top_k=1)

## Query the index
query = "What is the capital of Ghana?"
response = index.query_engine(query)
print(response)
```

## Error Handling
The DOSpacesReader class uses try-except blocks to catch and handle exceptions that may occur during various operations, such as connecting to the DigitalOcean Space, loading files, or persisting the index. If an error occurs, the relevant exception message will be printed to the console.

## Contributions
Contributions to the `DOSpacesReader` are welcome! If you find a bug, have a feature request, or want to contribute improvements, please open an issue or submit a pull request on the project's GitHub repository.

## License
The `DOSpacesReader` is released under the MIT License.