import gradio as gr
import traceback, logging, sys
import langchain
from workflow.langgraph_config import stocks_app
from config.logger_util import logger
langchain.debug = True

def process_analysis(user_query, history):
    if not user_query: yield history, "⚠️ Enter a query."; return

    history += [[user_query, ""]]
    try:
        # Stream from LangGraph
        for output in stocks_app.stream({"input": user_query}):
            for node, value in output.items():
                if "output" in value:
                    history[-1][1] = value["output"]
                elif "decision" in value:
                    history[-1][1] = f"*⚙️ Intent: {value['decision'].upper()}*\n\n"
                yield history, ""
    except Exception:
        yield history, f"### ❌ Error\n```python\n{traceback.format_exc()}\n```"

with gr.Blocks(theme="soft", title="StocksPredictor AI") as demo:
    gr.Markdown("# 📈 StocksPredictor AI\nIdentify breakouts or audit your portfolio.")

    chatbot = gr.Chatbot(label="Analysis History", height=450)
    error_box = gr.Markdown("")
    user_input = gr.Textbox(placeholder="e.g., 'Find 5 breakout stocks'", lines=2, label="Query")
    submit_btn = gr.Button("🚀 Run Analysis", variant="primary")

    # Mapping logic to a single reusable trigger
    run_event = {"fn": process_analysis, "inputs": [user_input, chatbot], "outputs": [chatbot, error_box]}

    submit_btn.click(**run_event).then(lambda: "", None, user_input)
    user_input.submit(**run_event).then(lambda: "", None, user_input)

if __name__ == "__main__":
    demo.launch(inline=True, share=True, debug=True)