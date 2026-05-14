import os
import requests
import time
import logging
from crewai import LLM
from config.settings import OLLAMA_BASE_URL

logger = logging.getLogger("OllamaService")


os.environ["OPENAI_API_KEY"] = "NA"


def get_llm_with_reconnect(
    model_name="ollama/llama3.1",
    base_url=OLLAMA_BASE_URL
):

    max_retries = 5

    for i in range(max_retries):
        try:
            response = requests.get(base_url, timeout=5)

            if response.status_code == 200:
                logger.info("✅ Ollama Connected")

                return LLM(
                    model=model_name,
                    base_url=base_url,
                    timeout=300,
                    max_retries=3
                )

        except requests.exceptions.ConnectionError:
            logger.warning(f"Retrying Ollama... {i+1}/{max_retries}")
            time.sleep(5)

    raise ConnectionError("Could not connect to Ollama")