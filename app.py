from config.logging_config import setup_logging
from graph.workflow import build_workflow
from ui.gradio_app import launch_ui

logger = setup_logging()

logger.info("🚀 Starting StocksPredictor AI")
logger.info("🧠 Building workflow")

stocks_app = build_workflow()

logger.info("🌐 Launching UI")
launch_ui(stocks_app)