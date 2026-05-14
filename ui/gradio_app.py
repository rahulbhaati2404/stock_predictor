import gradio as gr
import traceback



def process_analysis(stocks_app, user_query, history):
    if not user_query:
        yield history, "⚠️ Enter a query"
        return

    history += [[user_query, ""]]

    try:
        for output in stocks_app.stream({"input": user_query}):
            for node, value in output.items():
                if "output" in value:
                    history[-1][1] = value["output"]

                elif "decision" in value:
                    history[-1][1] = (
                        f"*Intent: {value['decision']}*"
                    )

                yield history, ""

    except Exception:
        yield history, traceback.format_exc()



def launch_ui(stocks_app):
    with gr.Blocks(
        theme="soft",
        title="StocksPredictor AI"
    ) as demo:

        gr.Markdown("# 📈 StocksPredictor AI")

        chatbot = gr.Chatbot(
            label="Analysis History",
            height=450
        )

        error_box = gr.Markdown("")

        user_input = gr.Textbox(
            placeholder="Find top 5 breakout stocks",
            lines=2,
            label="Query"
        )

        submit_btn = gr.Button(
            "🚀 Run Analysis",
            variant="primary"
        )

        run_event = {
            "fn": lambda q, h: process_analysis(stocks_app, q, h),
            "inputs": [user_input, chatbot],
            "outputs": [chatbot, error_box]
        }

        submit_btn.click(**run_event)
        user_input.submit(**run_event)

    demo.launch(debug=True, share=True)