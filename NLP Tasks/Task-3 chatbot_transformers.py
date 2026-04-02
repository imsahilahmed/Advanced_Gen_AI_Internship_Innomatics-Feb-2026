from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "microsoft/DialoGPT-medium"

print(f"Loading tokenizer  : {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

print(f"Loading model      : {MODEL_NAME}")
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()

print("Model and tokenizer loaded successfully!\n")


def generate_response(user_input, conversation_history, max_new_tokens=150):
    new_input_ids = tokenizer.encode(
        user_input + tokenizer.eos_token,
        return_tensors="pt"
    )

    if conversation_history is not None:
        input_ids = torch.cat([conversation_history, new_input_ids], dim=-1)
    else:
        input_ids = new_input_ids

    if input_ids.shape[-1] > 1000:
        input_ids = input_ids[:, -1000:]

    attention_mask = torch.ones_like(input_ids)

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            top_k=50,
            top_p=0.92,
            temperature=0.75,
            repetition_penalty=1.3
        )

    generated_tokens = output_ids[:, input_ids.shape[-1]:]

    response_text = tokenizer.decode(
        generated_tokens[0],
        skip_special_tokens=True
    ).strip()

    if not response_text:
        response_text = "I'm not sure I understood that. Could you rephrase?"

    return response_text, output_ids


def run_chatbot():
    print("=" * 55)
    print("   Transformer Chatbot — Powered by DialoGPT-medium")
    print("=" * 55)
    print("  Type your message and press Enter to chat.")
    print("  Type 'exit' or 'quit' to end the session.")
    print("-" * 55)

    print("\nChatbot: Hello! I am your AI assistant. How can I help you today?\n")

    conversation_history = None

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print("Chatbot: Please type something so I can respond!\n")
            continue

        if user_input.lower() in ["exit", "quit"]:
            print("\nChatbot: Thank you for chatting with me. Goodbye!")
            print("-" * 55)
            break

        response, conversation_history = generate_response(
            user_input,
            conversation_history
        )

        print(f"\nChatbot: {response}\n")


if __name__ == "__main__":
    run_chatbot()
