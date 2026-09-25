from openai import OpenAI

# Configure the client to point to your university's Open WebUI instance
client = OpenAI(
    base_url="https://app-mathllm.cloud.sdu.dk/api",  # Must end in /api or /api/v1
    api_key="sk-335ecbf9d39940629b7884a4ade31a8e",
)

# Send a prompt to a model
response = client.chat.completions.create(
    model="mistral:latest",  # Use the exact model name/ID shown in your web UI drop-down
    messages=[
        {"role": "user", "content": "Give me the fibunacci sequence"}
    ]
)

print(response.choices[0].message.content)