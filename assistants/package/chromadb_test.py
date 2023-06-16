import chromadb

# Step 1: Get the Chroma Client
chroma_client = chromadb.Client()

# Step 2: Create a collection
collection = chroma_client.create_collection(name="story_collection")

s1 = "assistants\package\story1.txt"
s2 = "assistants\package\story2.txt"

# Step 3: Read the contents of the story text files into strings
with open(s1, 'r') as file:
    story1_text = file.read()

with open(s2, 'r') as file:
    story2_text = file.read()

# Step 4: Add the stories to the collection
collection.add(
    documents=[story1_text, story2_text],
    ids=["story1", "story2"]
)

# Step 5: Query the collection with the question about horses
results = collection.query(
    query_texts=["which is talking about horses"],
    n_results=2
)

for id in results['ids'][0]:
    print(id)

