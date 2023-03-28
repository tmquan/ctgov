import gradio as gr
import pandas as pd

df = pd.read_csv("ctgov_437713_20230321.csv", index_col="nct_id")

target_col = "brief_title"
 
def search_func(source_col, elem, k=10, index_col = "nct_id"):
    json_dict = {}
    if index_col == source_col:
        if elem in df.index.tolist():
            target_val = df.loc[elem, target_col]
            print(f"Element {elem} found in column '{source_col}'. ",
                  f"Value in column '{target_col}': {target_val}")
            json_dict["source_index"] = elem
            json_dict["source_col"] = source_col
            json_dict["target_col"] = target_col
            json_dict["top_k"] = k
            json_dict["source_found"] = True
            return elem, target_val, json_dict
        else:
            print(f"Element {elem} not found in column '{source_col}'. ")
            json_dict["source_index"] = elem
            json_dict["source_col"] = source_col
            json_dict["target_col"] = target_col
            json_dict["source_found"] = False
            return elem, "Not Found", json_dict

iface = gr.Interface(
    fn=search_func,
    inputs=[
        gr.Textbox(label=f"Source column"),
        gr.Textbox(label=f"Source NCT_ID"),
        gr.Textbox(label=f"Number of similar trials"),
    ],
    outputs=[
        gr.Textbox(label=f"Source NCT_ID"),
        gr.Textbox(label=f"Source content at {target_col}"),
        gr.Json(label=f"Source content at {target_col}")
    ],
    examples=[
        ["nct_id", "NCT01258803", 5],
        ["nct_id", "NCT01254474", 5],
        ["nct_id", "BCT01222351", 5],
        ["nct_id", "BCT01222351", 5],
    ],
    title="Similar trial search",
    description="Enter an NCT_ID to extract it from the list.",
)

iface.launch()
