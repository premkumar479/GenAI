import requests

def main():
    print("Connecting to Ollama...")
    print("Model: Llama 3.2")
    print("Generating AI response...\n")

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "llama3.2",
        "prompt": "Explain Artificial Intelligence in simple words. Include its definition, working, real-life applications, advantages and disadvantages.",
        "stream": False
    }

    try:
        response = requests.post(
            url,
            json=data,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        print("=" * 60)
        print("              LLM RESPONSE")
        print("=" * 60)

        print(result["response"])

        print("=" * 60)
        print("Response generated successfully!")

    except requests.exceptions.ConnectionError:
        print("Error: Ollama is not running.")

    except Exception as error:
        print("Error:", error)


if __name__ == "__main__":
    main()