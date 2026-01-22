# Import the official OpenAI library
from openai import OpenAI

# Load API key from OpenAI
API_KEY = "YOUR_OPENAI_API_KEY"
client = OpenAI(api_key=API_KEY)

# Determine a maximum conversation length
MAX_HISTORY_LENGTH = 10
# Track the turn count and running summary
turn_count = 0
running_summary = ""

# Create a dictionary of personality traits for the AI
PERSONAS = {
    "pirate": "You are a pirate captain. Answer all questions with a pirate accent, arrr!",
    "professor": "You are a formal, academic professor. Answer all questions with precise, academic language.",
    "robot": "You are a sarcastic robot. Your answers are brief, logical, and slightly annoyed.",
    "default": "You are a helpful assistant. Answer all questions clearly and concisely."
}

### LEGACY CODE FOR GPT-3.5 - GPT-4 MODELS ###
## Make the API call to the GPT model
#response = client.chat.completions.create(
#    model="gpt-5",
#    messages=[{"role": "user", "content": prompt}]
#)
#
# Print the AI's response
#print("AI:", response.choices[0].message.content)

# Ask the user to choose a persona
choice = input("Choose a character (pirate, professor, robot): ")

if choice in PERSONAS:
    system_prompt = PERSONAS[choice]
else:
    system_prompt = PERSONAS["default"]

# Message structure for system prompt and conversation start
messages = [
    {"role": "system", "content": system_prompt}
]

# Ask the user if they want multi-response mode
mode = input("Multi-response mode? (y/n): ")

while True:
    # Get a prompt from the user
    prompt = input("You: ")

    # Exit upon user command, summarize, or adjust memory length
    if prompt.lower() in ['exit', 'quit']:
        break
    elif prompt.lower() in ['/summary']:
        prompt = "Provide a concise summary of our conversation so far."
    elif prompt.lower().startswith('/memory '):
        MAX_HISTORY_LENGTH = int(prompt.split(' ')[1])
        print(f"Memory length set to {MAX_HISTORY_LENGTH} messages.")
        continue

    # Print the AI's bullet list response
    if mode.lower() != 'n':
        prompt = f"Answer in exactly 3 bullet points:\n{prompt}"

    # Update the messages with user prompt to retain chat history
    messages.append({"role": "user", "content": prompt})

    # Manage conversation history length
    if len(messages) > MAX_HISTORY_LENGTH:
        # Remove oldest messages to maintain context length, but keep the system prompt
        messages = [messages[0]] + messages[-MAX_HISTORY_LENGTH:]
    # Every 10 turns, ask for a summary to condense context. Retain important facts to keep context manageable and tokens low.
    if turn_count > 0 and turn_count % 10 == 0:
        # Every 10 turns, ask for a summary to condense context
        summary_prompt = f"Please provide a concise, one-paragraph summary of the following conversation, retaining key facts: {messages}"
        try: 
            # Try to make the API call to the GPT model
            response = client.responses.create(
                model="gpt-5",
                input=summary_prompt
            )
            # Update the running summary
            running_summary = response.output_text

            # Reset messages to only include system prompt and summary
            messages = [messages[0]] + [{"role": "system", "content": f"Summary of the conversation so far: {running_summary}"}] 
            + messages[-MAX_HISTORY_LENGTH:]

        except Exception as e:
            # Provide failsafe if above API call fails
            print("AI: Sorry, something went wrong... {e}")

            # Remove the failed user prompt
            messages.pop()      
            break

    # Make the API call to the GPT model for the original prompt
    try: 
        # Try to make the API call to the GPT model
        response = client.responses.create(
            model="gpt-5",
            input=messages
        )
        # Save the AI's response to the messages for context retention
        ai_text = response.output_text
        print("AI:", ai_text)

        messages.append({"role": "assistant", "content": ai_text})
    except Exception as e:
        # Provide failsafe if above API call fails
        print("AI: Sorry, something went wrong... {e}")

        # Remove the failed user prompt
        messages.pop()
    turn_count += 1
