from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# chunk_size = how many approx token in one chunk; overlap = overlapping part between two chunks
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)

def load_and_chunk(file_path: str):
    # SimpleDirectoryReader reads file based on file extension
    docs = SimpleDirectoryReader(input_files=[file_path]).load_data()
    nodes = splitter.get_nodes_from_documents(docs)
    return nodes   # each node has: node.get_content(), node.metadata