import gradio as gr
import numpy as np

import os
os.environ['TRANSFORMERS_CACHE'] = 'cache'

import pandas as pd
import numpy as np 
import json
try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = lambda x: x
    
from txtai.embeddings import Embeddings
from txtai.pipeline import Similarity
from txtai.pipeline import Tabular
from txtai.workflow import Task
from txtai.workflow import Workflow
from huggingface_hub import snapshot_download

class SemanticSearch(object):
    def __init__(
        self,
        filename="ctgov_34983_20230417",
        columns=[
            "brief_title",
            "official_title",
            "brief_summaries",
            "detailed_descriptions",
            "criteria",
        ], 
        ckptlist=[
            "sentence-transformers/multi-qa-mpnet-base-dot-v1",
        ],
        rerun=True,
    ):
        self.filename = filename
        self.columns = columns
        self.ckptlist = ckptlist
        
        for ckptpath in self.ckptlist:
            snapshot_download(repo_id=ckptpath,
                            repo_type="model",
                            cache_dir="cache") 
            self.embeddings = Embeddings({
                "method": "transformers",
                "path": ckptpath, 
                "content": True, 
                "object": True
            })
            indexfile = f'{filename}_{ckptpath.replace("/", "-")}.index'
            if os.path.exists(indexfile) and rerun is False:
                print("Indexed and Cached!")
                self.embeddings.load(indexfile)
            else:
                print("Need to rerun or Indices and Caches dont exist, run them!")
                
                # Create tabular instance mapping input.csv fields
                tabular = Tabular(idcolumn="nct_id", textcolumns=columns, content=True)
                
                # Create workflow
                workflow = Workflow([Task(tabular)])

                # Index subset of CORD-19 data
                data = list(workflow([f'{filename}.csv']))
                # print(data[:1])
                self.embeddings.index(data)
                self.embeddings.save(indexfile)
                print("Indexing and Caching finished for the 1st time!")

            # prompt = "hypertension"
            # query = f'select {", ".join([column for column in self.columns])} from txtai where similar({prompt})'
            # for result in self.embeddings.search(query):
            #     print(json.dumps(result, default=str, indent=2))

    def search_func(self, prompttext, pretrained="sentence-transformers/multi-qa-mpnet-base-dot-v1", limit=10):
        assert pretrained in self.ckptlist
        query = f'select {", ".join(["nct_id"] + [column for column in self.columns])} from txtai where similar({prompttext})'
        result = self.embeddings.search(query, limit)
        return result
    
    def launch_interface(self, *args, **kwargs):
        interface = gr.Interface(
            fn=lambda *args, **kwargs: self.search_func(*args, **kwargs),
            inputs=[
                gr.Textbox(label=f"Source prompt text"),
                gr.Dropdown(self.ckptlist, label=f"Pretrained model"),
                gr.Slider(1, 20, value=5, label=f"Number of similar trials", step=1),
            ],
            outputs=[
                gr.Json(label=f"Similar trials if found")
            ],
            examples=[
                ["hypertension", "sentence-transformers/multi-qa-mpnet-base-dot-v1", 3],
                ["diabetes", "sentence-transformers/multi-qa-mpnet-base-dot-v1", 2],
            ],
            title="Semantic Search on Clinical Trial Data",
            description="Enter a prompt",
        )

        interface.launch(*args, **kwargs)
        
def main():
    trial_search = SemanticSearch(
        filename="ctgov_34983_20230417",
        columns=[
            "brief_title",
            "official_title",
            "brief_summaries",
            "detailed_descriptions",
            "criteria",
        ], 
        ckptlist=[
            "sentence-transformers/multi-qa-mpnet-base-dot-v1",
        ],
        rerun=False,
    )
    trial_search.launch_interface(server_name="localhost")

if __name__ == "__main__":
    main()
