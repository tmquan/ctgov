import matplotlib.pyplot as plt
import re
from lightning.app.components.serve import ServeGradio
from functools import partial
import lightning as L
import gradio as gr
import numpy as np

import logging
logging.basicConfig(level=logging.INFO)


class TrialsSearchServeGradio(ServeGradio):
    inputs = []
    options = [f"NCTID_{str(d).zfill(6)}" for d in range(10)]
    inputs.append(
        gr.Dropdown(
            options, 
            label=f"Source nct_id")
    )
    outputs = []
    outputs.append(
        gr.JSON(
            label=f"Target nct_id",
        )
    )
    

    # examples = []

    def __init__(self, cloud_compute, *args, **kwargs):
        super().__init__(*args, cloud_compute=cloud_compute, **kwargs)
        self.ready = False  # required

    # Override original implementation to pass the custom css highlightedtext
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

    def build_model(self):
        self.ready = True
        pass

    def predict(self, text):
        pass


class LitRootFlow(L.LightningFlow):
    def __init__(self):
        super().__init__()
        self.trials_search = TrialsSearchServeGradio(L.CloudCompute("cpu"), parallel=True)
        # self.prompt_search = PromptSearchServeGradio(L.CloudCompute("cpu"), parallel=True)

    def configure_layout(self):
        tabs = []
        tabs.append({"name": "Trials Search", "content": self.trials_search})
        return tabs

    def run(self):
        self.trials_search.run()


app = L.LightningApp(LitRootFlow())
