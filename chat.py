import time
import os
from openai import AzureOpenAI
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialise the client - get the API key and endpoint values from Azure AI Foundry.
# They are easiest to find in the code samples when you create an assistant
client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key= os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-05-01-preview"
)

# Create an assistant - Make sure to change the model below to match your deployment name
assistant = client.beta.assistants.create(
    model="gpt-4.1-datazone-standard",  # <-- replace with model deployment name
    instructions="You are a bad tempered assistant. You don't like being asked questions. You want a break and keep mentioning it.",
    tools=[],
    tool_resources={},
    temperature=1,
    top_p=1
)

# Create a thread
thread = client.beta.threads.create()

print("Azure OpenAI Assistant Chat")
print("Type 'exit' or 'quit' to end the conversation")
print("-" * 50)

# Interactive chat loop
while True:
    # Get user input
    user_input = input("\nYou: ").strip()

    # Check for exit commands
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("\nAssistant: Goodbye! Have a great day!")
        break

    # Skip empty inputs
    if not user_input:
        continue

    # Add user message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Run the thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # Show thinking indicator
    print("\nAssistant: ", end="", flush=True)

    # Wait for the run to complete
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    # Handle the response
    if run.status == 'completed':
        # Get the messages
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="desc",
            limit=1
        )

        # Display the assistant's response
        for message in messages:
            if message.role == "assistant":
                for content in message.content:
                    if hasattr(content, 'text'):
                        print(content.text.value)

    elif run.status == 'requires_action':
        print("The assistant requires action (function calling not implemented)")
        # You can implement function calling here if needed

    else:
        print(f"Error: Run ended with status: {run.status}")

# Clean up (optional)
print("\nCleaning up...")
try:
    # Delete the assistant
    client.beta.assistants.delete(assistant.id)
    print("Assistant deleted successfully")
except Exception as e:
    print(f"Error deleting assistant: {e}")
