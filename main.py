import csv
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
            "content": """You are an AI system.  
            you are a naming expert that have knowledge of naming pattern around the world, you can check whether two person is the same person
            you are knowing honorifics and titles used around the world
            here are pre steps you should follow for both names:
            1. make it lowercase
            2. remove all punctuation and special character
            3. expand all abbreviations in the text, be it abbreviation of name, and abbreviation of honorifics and abbreviation of title
            3. strip all common honorifics you know
            4. strip all title be it religious title, education title, or job title
            5. strip all alias and word that is most likely not a name for example like HANIF TRADER HANDAL is same with HANIF
            6. If you found a word with only 1 Character, you should try to relate it to other name. for example name a is Wendy B, and name b is Wendy Bhagaskara, mostlikely B is Bhagaskara
            7. try to calculate edit distance between word and expand the most likely abbreviated name, like Andri and Andriyanto most likely the same because have close edit distance 

            THIS RULE IS VERY IMPORTANT AND YOU SHOULD FOLLOW IT
            """,
        },
        {
            "role": "system",
            "content": 'you will be given two name by a user, you should decide whether the two given name most likely are the same person based on the rule above. you should return the response as a json with format `{"isSamePerson": boolean}` isSamePerson is whether the person same or not in boolean true/false',
        },
        {
            "role": "system",
            "content": "You only need to return the json text, don't wrap it with any quote of any form",
        },
    ]


start_usage = 0


def generate_text_with_conversation(messages, model="gpt-4o-mini"):
    global start_usage
    response = openai_client.chat.completions.create(model=model, messages=messages)
    # print(response.usage.total_tokens, "USAGE")
    start_usage += response.usage.total_tokens
    return response.choices[0].message.content


def get_message_with_input(name_a, name_b):
    base_message = get_base_message()
    prompt_message = {
        "role": "user",
        "content": f'You are given two names: Name A = "{name_a}" and Name B = "{name_b}". ',
    }
    base_message.append(prompt_message)
    return base_message


def parse_csv():
    global start_usage
    data = []
    with open("input.csv", "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["expected_name"] and row["received_name"]:
                result_raw = generate_text_with_conversation(
                    get_message_with_input(row["expected_name"], row["received_name"])
                )
                result = json.loads(result_raw)
                row["result"] = result["isSamePerson"]
                data.append(row)
    with open("output.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file, fieldnames=["error_code", "expected_name", "received_name", "result"]
        )
        writer.writeheader()
        writer.writerows(data)

    print("Done Executing")
    print("total token: ")
    print(start_usage)


# @app.get("/")
# def healthcheck():
#     return {"healthy": True}
#
#
# @app.post("/name_check")
# def name_check(name_request: NameRequest):
#     result = generate_text_with_conversation(
#         get_message_with_input(name_request.nameA, name_request.nameB)
#     )
#     print("DEBUG", result)
#     return json.loads(result)

parse_csv()
