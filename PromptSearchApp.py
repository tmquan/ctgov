import gradio as gr
import numpy as np
from datasets import load_from_disk

import os
import torch
from transformers import AutoTokenizer, AutoModel

def _generate_embedding(
        text=None, 
        model=None,
        modelname=None,
        tokenizer=None, 
        size=256
    ):
    # print(modelname)
    # Split the text into smaller chunks to fit the BERT model_name's input size
    chunks = [text[i:i+size] for i in range(0, len(text), size)] # type: ignore
    # Generate BERT embeddings for each chunk and concatenate them
    embeddings = []
    for chunk in chunks:
        if "openai" in modelname: # type: ignore
            chunk_embedding = openai.Embedding.create(
                input=[chunk],
                model="text-embedding-ada-002"
            )['data'][0]['embedding']  # type: ignore
        else:
            # Tokenize the text
            tokens = tokenizer.encode(chunk, add_special_tokens=True)
            device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
            tokens = torch.tensor([tokens]).to(device)

            # Generate the BERT/GPT embeddings
            chunk_outputs = model(tokens)
            # Extract the tensor containing the embeddings
            chunk_embeddings = chunk_outputs.last_hidden_state
            # Average the embeddings over the sequence length to get a single vector for the chunk
            chunk_embedding = torch.mean(chunk_embeddings, dim=1).tolist()[0]
        embeddings.append(chunk_embedding)
    row_embedding = np.array([sum(x) for x in zip(*embeddings)])
    return row_embedding

class PromptSearch(object):
    def __init__(
        self, 
        filename="ctgov_437713_20230321",
        source_col="nct_id",
        target_col="brief_title",
        
    ):
        self.source_col = source_col
        self.target_col = target_col
        self.ds = load_from_disk(filename)
        self.df = self.ds.to_pandas()
        # Duplicate index column and set index to index
        self.df.index = self.df.set_index("nct_id")
        self.df = self.df.set_index("nct_id")
        self.options = [
            "emilyalsentzer/Bio_ClinicalBERT",
            "microsoft/biogpt"
        ]
        self.add_faiss_indices(self.options)
        
    def add_faiss_indices(self, options):
        for embedding_type in options:
            self.ds.add_faiss_index(column=embedding_type)

    def search_func(self, prompttext, pretrained="emilyalsentzer/Bio_ClinicalBERT", k=10):
        json_dict = {}
        
        # Run embedding for text
        cache_dir = os.path.join(os.path.curdir, 'cache')
        size = 256
        tokenizer = AutoTokenizer.from_pretrained(pretrained, cache_dir=cache_dir)
        model = AutoModel.from_pretrained(pretrained, cache_dir=cache_dir)
        device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        model.to(device)
        
        target_embed = _generate_embedding(
            prompttext, 
            model=model, 
            modelname=pretrained, 
            tokenizer=tokenizer, 
            size=size
        )
        # topk_similar
        scores, retrieved_examples = self.ds.get_nearest_examples(pretrained, target_embed, k=k)
        keys_similar = [self.source_col, self.target_col]
        topk_similar = {key: retrieved_examples[key] for key in keys_similar}
        json_dict = {
            "source_col"    : self.source_col,
            "target_col"    : self.target_col,
            "prompttext"    : prompttext,
            "pretrained"    : pretrained,
            "topk"          : k,
            "topk_similar"  : topk_similar,
        }
        return json_dict
      

    def launch_interface(self, *args, **kwargs):
        interface = gr.Interface(
            fn=lambda *args, **kwargs: self.search_func(*args, **kwargs),
            inputs=[
                gr.Textbox(label=f"Source prompt text"),
                gr.Dropdown(self.options, label=f"Pretrained model"),
                gr.Slider(1, 20, value=5, label=f"Number of similar trials", step=1),
            ],
            outputs=[
                gr.Json(label=f"Similar trials if found")
            ],
            examples=[
                ["diabetes", "emilyalsentzer/Bio_ClinicalBERT", 5],
                ["diabetes", "microsoft/biogpt", 5],
                ["hypertension", "emilyalsentzer/Bio_ClinicalBERT", 5],
                ["hypertension", "microsoft/biogpt", 5],
            ],
            title="Prompt Text Search",
            description="Enter a prompt",
        )

        interface.launch(*args, **kwargs)


def main():
    trial_search = PromptSearch()
    trial_search.launch_interface()

if __name__ == "__main__":
    main()
