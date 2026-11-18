import unittest

from llm_client import LLMClient


class FakeProvider:

    def generate(self, prompt):
        return "This is a fake AI response."


class TestLLMClient(unittest.TestCase):

    def test_generate_response(self):

        provider = FakeProvider()

        client = LLMClient(provider)

        result = client.generate("What is AI?")

        self.assertEqual(
            result,
            "This is a fake AI response."
        )


if __name__ == "__main__":
    unittest.main()