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

import gradio as gr

# Setup your blocks layout
with gr.Blocks(theme="soft", title="StocksPredictor AI") as demo:
    gr.Markdown("# 📈 StocksPredictor AI\nIdentify breakouts or audit your portfolio.")

    chatbot = gr.Chatbot(label="Analysis History", height=450, type="messages")
    error_box = gr.Markdown("")
    user_input = gr.Textbox(placeholder="e.g., 'Find 5 breakout stocks'", lines=1, label="Query") # Changed lines=1 to make Enter feel natural
    submit_btn = gr.Button("🚀 Run Analysis", variant="primary")

    # Helper function 1: Instantly shows user message on the right and freezes UI controls
    def user_submit_handler(message, history):
        if not message.strip():
            return "", history, gr.update(interactive=True), gr.update(interactive=True)
            
        # Append the user's chat message to the history layout stack
        history.append({"role": "user", "content": message})
        
        # Returns: empty text input, updated history, disabled text box, disabled button
        return "", history, gr.update(interactive=False), gr.update(interactive=False)

    # Helper function 2: Runs the heavy processing, then safe-unlocks the UI controls
    def bot_response_handler(history):
        # 1. Extract the last query message sent by user
        user_query = history[-1]["content"] if history else ""
        
        # 2. Run your existing LangGraph application generation flow
        # Ensure your process_analysis matches this signature or yields streaming dictionaries
        updated_history, error_msg = process_analysis(user_query, history)
        
        # Returns: the final chat history, any errors, re-enabled text box, re-enabled button
        return updated_history, error_msg, gr.update(interactive=True), gr.update(interactive=True)


    # ==========================================
    # EVENT TRIGGER FLOWS (Sequential Steps)
    # ==========================================

    # Triggers when clicking the button
    submit_btn.click(
        fn=user_submit_handler,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot, user_input, submit_btn]
    ).then(
        fn=bot_response_handler,
        inputs=[chatbot],
        outputs=[chatbot, error_box, user_input, submit_btn]
    )

    # Triggers when pressing Enter inside the Textbox
    user_input.submit(
        fn=user_submit_handler,
        inputs=[user_input, chatbot],
        outputs=[user_input, chatbot, user_input, submit_btn]
    ).then(
        fn=bot_response_handler,
        inputs=[chatbot],
        outputs=[chatbot, error_box, user_input, submit_btn]
    )

if __name__ == "__main__":
    demo.launch(inline=True, share=True, debug=True)