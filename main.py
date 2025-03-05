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
            "content": "You are an AI system.  you are a naming expert that have knowledge of naming pattern around the world, you have expertise and knowledge about  name because you know the culture of different countries, the prefix usually used, and the honorifics. you should also account for a typo, you should also account for a repeated name because first name and last name is required, also ignore the text casing. also you should remember about abbreviation both in name and honorifics, for example SAUDARA / SODARA can be SDR and Caesar can be C.",
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
