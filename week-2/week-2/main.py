import os
from dotenv import load_dotenv

from llm_client import (
    LLMClient,
    OllamaProvider,
    GeminiProvider
)


def main():

    load_dotenv()

    print("WEEK-2: PROVIDER-AGNOSTIC LLM CLIENT")
    print("------------------------------------")

    provider_name = input(
        "Choose provider (gemini/ollama): "
    ).strip().lower()

    try:

        if provider_name == "ollama":

            provider = OllamaProvider(
                model="llama3.2"
            )

            print("\nConnected to Ollama (Llama 3.2).")

        elif provider_name == "gemini":

            provider = GeminiProvider(
                os.getenv("GEMINI_API_KEY")
            )

            print("\nConnected to Gemini.")

        else:

            print("Invalid provider. Choose ollama or gemini.")
            return

        client = LLMClient(provider)

        prompt = input("\nEnter your question: ")

        if not prompt.strip():
            print("Question cannot be empty.")
            return

        print("\nGenerating response...\n")

        answer = client.generate(prompt)

        print("LLM Response:")
        print("------------------------------")
        print(answer)
        print("------------------------------")

    except requests.exceptions.ConnectionError:
        print("Error: Ollama is not running.")

    except Exception as error:
        print(f"\nAn error occurred: {error}")


if __name__ == "__main__":
    import requests
    main()