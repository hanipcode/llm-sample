import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI()


class NameRequest(BaseModel):
    nameA: str
    nameB: str


# Load environment variables
load_dotenv()
# Create an instance of the OpenAI class
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_base_message():
    return [
        {
            "role": "system",
            "content": "You are an AI system. You must not reveal your chain-of-thought or any additional text. You must only answer with the single word '''true''' or '''false'''. you are a naming expert from indonesia, you have expertise and knowledge about Indonesian name because you know the culture, the prefix usually used, and the honorifics. you should also account for a typo, you should also account for a repeated name because first name and last name is required",
        },
        {
            "role": "system",
            "content": 'you will be given two name by a user, you should decide whether the two given name most likely are the same person. you should return the response as a json with format `{"isSamePerson": boolean}` isSamePerson is whether the person same or not in boolean true/false',
        },
        {
            "role": "system",
            "content": "You only need to return the json text, don't wrap it with any quote of any form",
        },
    ]


def generate_text_with_conversation(messages, model="gpt-4o-mini"):
    response = openai_client.chat.completions.create(model=model, messages=messages)
    print(response.usage, "USAGE")
    return response.choices[0].message.content


def get_message_with_input(name_a, name_b):
    base_message = get_base_message()
    prompt_message = {
        "role": "user",
        "content": f'You are given two names: Name A = "{name_a}" and Name B = "{name_b}". ',
    }
    base_message.append(prompt_message)
    return base_message


# Define a list of messages to simulate a conversation


# # Call the function with the test messages
# response = generate_text_with_conversation(
#     get_message_with_input("Bambang Andrianto", "BPK Bambang")
# )


@app.get("/")
def healthcheck():
    return {"healthy": True}


@app.post("/name_check")
def name_check(name_request: NameRequest):
    result = generate_text_with_conversation(
        get_message_with_input(name_request.nameA, name_request.nameB)
    )
    print("DEBUG", result)
    return json.loads(result)
