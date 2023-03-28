import gradio as gr
import numpy as np
from datasets import load_from_disk

class CTrialSearch(object):
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

    def search_func(self, elem, pretrained="emilyalsentzer/Bio_ClinicalBERT", k=10):
        json_dict = {}
        if elem in self.df.index.tolist():
            target_value = self.df.loc[elem, self.target_col]
            target_embed = np.fromstring(self.df.loc[elem, pretrained]).astype(np.float32)
            # topk_similar
            scores, retrieved_examples = self.ds.get_nearest_examples(pretrained, target_embed, k=k)
            keys_similar = [self.source_col, self.target_col]
            topk_similar = {key: retrieved_examples[key] for key in keys_similar}
            json_dict = {
                "source_index"  : elem,
                "source_col"    : self.source_col,
                "source_found"  : True,
                "target_col"    : self.target_col,
                "target_value"  : target_value,
                "pretrained"    : pretrained,
                "topk"          : k,
                "topk_similar"  : topk_similar,
            }
            return elem, target_value, json_dict
        else:
            json_dict = {
                "source_index"  : elem,
                "source_col"    : self.source_col,
                "source_found"  : False,
                "target_col"    : self.target_col,
                "target_value"  : None,
                "pretrained"    : pretrained,
                "topk"          : k,
                "topk_similar"  : None,
            }
            return elem, "Not Found", json_dict

    def launch_interface(self):
        interface = gr.Interface(
            fn=lambda *args, **kwargs: self.search_func(*args, **kwargs),
            inputs=[
                # gr.Textbox(label=f"Source column"),
                gr.Textbox(label=f"Source NCT_ID"),
                gr.Dropdown(self.options, label=f"Pretrained model"),
                gr.Slider(1, 20, value=5, label=f"Number of similar trials", step=1),
            ],
            outputs=[
                gr.Textbox(label=f"Source NCT_ID"),
                gr.Textbox(label=f"Source content at {self.target_col}"),
                gr.Json(label=f"Similar trials if found")
            ],
            examples=[
                ["NCT01258803", "emilyalsentzer/Bio_ClinicalBERT", 5],
                ["NCT01254474", "microsoft/biogpt", 5],
                ["BCT01258803", "emilyalsentzer/Bio_ClinicalBERT", 5],
                ["BCT01254474", "microsoft/biogpt", 5],
            ],
            title="Similar trial search",
            description="Enter an NCT_ID to extract it from the list.",
        )

        interface.launch()


def main():
    trial_search = CTrialSearch()
    trial_search.launch_interface()


if __name__ == "__main__":
    main()
