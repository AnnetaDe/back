import json


class GPTHandler:
    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ):
        """
        Initialize the GPTHandler with API key and default settings.

        :param api_key: OpenAI API key.
        :param model: The model to use (e.g., "gpt-4" or "gpt-3.5-turbo").
        :param max_tokens: Maximum tokens for the response.
        :param temperature: Controls randomness of the output (0.0 - deterministic, 1.0 - creative).
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate_question(self, subject: str, level: int) -> str:
        """
        Generate a response from GPT for the given prompt.

        :param prompt: The input prompt for the model.
        :return: The model's response as a string.
        """
        import openai

        openai.api_key = self.api_key  # Set the API key
        client = openai.Client()

        level = level
        prompt = (
            f"Generate a unique JSON object for a multiple-choice question on '{subject}' "
            f"with difficulty {level} (1 = easy, 4 = very hard)."
            "JSON includes:\n"
            '{"question":"text","choices":{"1":"1","2":"2","3":"3","4":"4"},'
            '"subject":"subject","answer":"Correct option (1, 2, 3, or 4)","level":1}. '
            "Ensure the JSON is valid, complete,no errors, check for JSONDecodeError."
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that generates quiz questions for students. "
                        "The questions are for academic testing and should be unique and accurate.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            content = response.choices[0].message.content

            if content is None:
                raise ValueError("Received empty response from the model")
            return content.strip()

        except Exception as e:
            raise ValueError(f"Failed to generate response: {e}")
