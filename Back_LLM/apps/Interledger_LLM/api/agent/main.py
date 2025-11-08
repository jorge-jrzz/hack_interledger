from openai import OpenAI
client = OpenAI()

response = client.responses.create(
    model="gpt-5-nano",
    input="que dia es hoy?"
)

print(response.output_text)