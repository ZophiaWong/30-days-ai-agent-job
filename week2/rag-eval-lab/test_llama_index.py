from llama_index.core import SimpleDirectoryReader

docs = SimpleDirectoryReader("./data/processed/md/langgraph_docs").load_data()
print(len(docs))
