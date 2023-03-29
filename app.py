from functools import partial
import gradio as gr
import requests
import torch
from PIL import Image
from datasets import load_from_disk
import lightning as L
from lightning.app.components.serve import ServeGradio

from app_v1 import TrialsSearch
from app_v2 import PromptSearch

class TrialsSearchServeGradio(ServeGradio):
    options = [
        "emilyalsentzer/Bio_ClinicalBERT",
        "microsoft/biogpt"
    ]    
    inputs=[
        gr.Textbox(label=f"Source NCT_ID"),
        gr.Dropdown(options, label=f"Pretrained model"),
        gr.Slider(1, 20, value=5, label=f"Number of similar trials", step=1),
    ]
    outputs=[
        gr.Json(label=f"Similar trials if found")
    ]
    examples=[
        ["NCT01258803", "emilyalsentzer/Bio_ClinicalBERT", 5],
        ["NCT01254474", "microsoft/biogpt", 5],
        ["BCT01258803", "emilyalsentzer/Bio_ClinicalBERT", 5],
        ["BCT01254474", "microsoft/biogpt", 5],
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._model = None
        self.ready = False

    def build_model(self):
        model = TrialsSearch(
            filename="ctgov_437713_20230321",
            source_col="nct_id",
            target_col="brief_title",
        )
        self.ready = True
        return model
    
    def predict(self, elem, pretrained="emilyalsentzer/Bio_ClinicalBERT", k=10):
        return self._model.search_func(elem, pretrained, k)
    
    def run(self, *args, **kwargs):
        if self._model is None:
            self._model = self.build_model()

        # Partially call the prediction
        fn = partial(self.predict, *args, **kwargs)
        fn.__name__ = self.predict.__name__
        gr.Interface(
            fn=fn,      
            inputs=self.inputs,
            outputs=self.outputs,
            examples=self.examples
        ).launch(
            server_name=self.host,
            server_port=self.port,
            enable_queue=self.enable_queue,
            share=False,
        )

class PromptSearchServeGradio(ServeGradio):
    options = [
        "emilyalsentzer/Bio_ClinicalBERT",
        "microsoft/biogpt"
    ]    
    inputs=[
        gr.Textbox(label=f"Source prompt text"),
        gr.Dropdown(options, label=f"Pretrained model"),
        gr.Slider(1, 20, value=5, label=f"Number of similar trials", step=1),
    ]
    outputs=[
        gr.Json(label=f"Similar trials if found")
    ]
    examples=[
        ["diabetes", "emilyalsentzer/Bio_ClinicalBERT", 5],
        ["diabetes", "microsoft/biogpt", 5],
        ["hypertension", "emilyalsentzer/Bio_ClinicalBERT", 5],
        ["hypertension", "microsoft/biogpt", 5],
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self._model = None
        self.ready = False

    def build_model(self):
        model = PromptSearch(
            filename="ctgov_437713_20230321",
            source_col="nct_id",
            target_col="brief_title",
        )
        self.ready = True
        return model
    
    def predict(self, elem, pretrained="emilyalsentzer/Bio_ClinicalBERT", k=10):
        return self._model.search_func(elem, pretrained, k)
    
    def run(self, *args, **kwargs):
        if self._model is None:
            self._model = self.build_model()

        # Partially call the prediction
        fn = partial(self.predict, *args, **kwargs)
        fn.__name__ = self.predict.__name__
        gr.Interface(
            fn=fn,      
            inputs=self.inputs,
            outputs=self.outputs,
            examples=self.examples
        ).launch(
            server_name=self.host,
            server_port=self.port,
            enable_queue=self.enable_queue,
            share=False,
        )
        

class LitRootFlow(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.trials_search = TrialsSearchServeGradio(parallel=True)
        self.prompt_search = PromptSearchServeGradio(parallel=True)

    def configure_layout(self):
        tabs = []
        tabs.append({"name": "Trials Search", "content": self.trials_search})
        tabs.append({"name": "Prompt Search", "content": self.prompt_search})
        return tabs

    def run(self):
        self.trials_search.run()
        self.prompt_search.run()

app = L.LightningApp(LitRootFlow())
# app = L.LightningApp(TrialsSearchServeGradio())