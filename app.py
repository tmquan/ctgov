from huggingface_hub import snapshot_download
from txtai.workflow import Workflow
from txtai.workflow import Task
from txtai.pipeline import Tabular
from txtai.pipeline import Similarity
from txtai.embeddings import Embeddings
from pprint import pprint
import json
import pandas as pd
import gradio as gr
import numpy as np
import geopy.distance
from geopy.geocoders import Nominatim
import os
os.environ['TRANSFORMERS_CACHE'] = 'cache'

try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(x): return x


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
                tabular = Tabular(idcolumn="nct_id",
                                  textcolumns=columns, content=True)

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

    def search_func(self, 
                    prompttext, 
                    pretrained="sentence-transformers/multi-qa-mpnet-base-dot-v1", 
                    location="Kendall MIT",
                    distance=200,
                    limit=None):
        assert pretrained in self.ckptlist
        query = f'select {", ".join(["nct_id"] + [column for column in self.columns])} from txtai where similar({prompttext})'
        results = self.embeddings.search(query, limit=35000)
        # pprint(results)
        filters = self.search_cond(results, location, distance)
        return filters

    def search_cond(self, 
                    results, 
                    location, 
                    distance):
        
        # Parse location into latitude and longitude using geopy
        geolocator = Nominatim(user_agent="my-app")
        location_obj = geolocator.geocode(location)
        if location_obj is None:
            raise ValueError(f"Could not find location: {location}")
        location_coords = (location_obj.latitude, location_obj.longitude)

        # Filter results based on distance from the location
        filtered_results = []
        for result in results:
            # Use the first location column available
            location_col = next((col for col in result.keys() if col in [
                                'city', 'state', 'zip', 'country']), None)
            if location_col is None:
                # No location column found, skip this result
                continue
            location_str = result[location_col]
            location_obj = geolocator.geocode(location_str)
            if location_obj is None:
                # Could not parse location, skip this result
                continue
            result_coords = (location_obj.latitude, location_obj.longitude)
            dist = geopy.distance.distance(location_coords, result_coords).km
            if dist <= distance:
                filtered_results.append(result)

        return filtered_results
    
    def launch_interface(self, *args, **kwargs):
        interface = gr.Interface(
            fn=lambda *args, **kwargs: self.search_func(*args, **kwargs),
            inputs=[
                gr.Textbox(label=f"Source prompt text"),
                gr.Dropdown(self.ckptlist, label=f"Pretrained model"),
                gr.Textbox(label=f"Location"),
                gr.Slider(1, 2000, value=100,
                          label=f"Within (kms)", step=10),
            ],
            outputs=[
                gr.Json(label=f"Similar trials if found")
            ],
            examples=[
                ["hypertension", "sentence-transformers/multi-qa-mpnet-base-dot-v1", "San Francisco", 500],
                ["hypertension", "sentence-transformers/multi-qa-mpnet-base-dot-v1", "Cambridge", 500],
                ["diabetes", "sentence-transformers/multi-qa-mpnet-base-dot-v1", "Miami", 500],
                ["diabetes", "sentence-transformers/multi-qa-mpnet-base-dot-v1", "Boston", 500],
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
            "city",
            "state",
            "zip",
            "country",
        ],
        ckptlist=[
            "sentence-transformers/multi-qa-mpnet-base-dot-v1",
        ],
        rerun=False,
    )
    trial_search.launch_interface(server_name="localhost")


if __name__ == "__main__":
    main()
