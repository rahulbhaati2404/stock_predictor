import gradio as gr
import traceback
import logging
import sys

# Import your LangGraph workflow from the core folder
from core.workflow import stocks_app 

# Global Debug & Compact Logging
logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("StocksApp")

def process_analysis(user_query, history):
    if not user_query: 
        yield history, "⚠️ Enter a query."
        return

    # Add the user query to history with an initial loading message
    history.append([user_query, "⏳ **System:** Waking up Agents..."])
    yield history, ""

    current_response = ""

    try:
        # Stream from LangGraph node by node
        for output in stocks_app.stream({"input": user_query}):
            for node, value in output.items():
                
                # --- PROGRESS LOGGING LOGIC ---
                # Match the LangGraph node name to a user-friendly message
                if node == "router":
                    intent = value.get("decision", "UNKNOWN")
                    current_response += f"✅ **Stage 1:** Intent classified as `{intent}`.\n\n"
                
                elif node == "search_web_node":
                    current_response += "🔍 **Stage 2:** Web Scraper activated. Hunting for breakout stocks...\n\n"
                
                elif node == "analysis_node":
                    current_response += "📊 **Stage 2:** Technical Analyst Agent is reviewing the charts and news...\n\n"
                
                elif node == "portfolio_manager_node":
                    current_response += "🛡️ **Stage 2:** Portfolio Manager Agent is auditing risk metrics...\n\n"

                # Update the UI with the current progress
                history[-1][1] = current_response
                yield history, ""

                # --- FINAL OUTPUT LOGIC ---
                # If the node returns the final 'output' from the Agent, append it
                if "output" in value:
                    current_response += f"---\n### 🎯 Final Report\n{value['output']}"
                    history[-1][1] = current_response
                    yield history, ""

    except Exception:
        history[-1][1] = f"### ❌ Error during execution\n```python\n{traceback.format_exc()}\n```"
        yield history, ""

# 2. Compact UI Layout
with gr.Blocks(theme="soft", title="StocksPredictor AI") as demo:
    gr.Markdown("# 📈 StocksPredictor AI\nIdentify breakouts or audit your portfolio.")

    chatbot = gr.Chatbot(label="Analysis Terminal", height=500)
    error_box = gr.Markdown("")
    user_input = gr.Textbox(placeholder="e.g., 'Find Top 5 Breakouts' or 'Analyze RELIANCE'", lines=2, label="Market Query")
    submit_btn = gr.Button("🚀 Run Analysis", variant="primary")

    # Mapping logic to a single reusable trigger
    run_event = {"fn": process_analysis, "inputs": [user_input, chatbot], "outputs": [chatbot, error_box]}

    submit_btn.click(**run_event).then(lambda: "", None, user_input)
    user_input.submit(**run_event).then(lambda: "", None, user_input)

if __name__ == "__main__":
    print("🚀 Starting Gradio Server...")
    demo.launch(inline=False, share=False, debug=True)