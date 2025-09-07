from nicegui import ui
import asyncio
import requests

from .sentence import run_sentence_transformer


# Chatbot logic paired with meta-llama model
async def chatbot_response(query: str) -> str:
    await asyncio.sleep(0.2)  # simulate processing delay
    res = requests.get(
        "http://localhost:8000/agent",
        params={'q': query},
        headers={"accept": "application/json"},
    )

    # Safe handling
    try:
        chunk = res.json()
    except Exception:
        chunk = {"answer": res.text}

    answer_chunk = chunk.get("answer", "⚠️ No answer received")
    conclusion = run_sentence_transformer(messy=answer_chunk, query=query)
    return f"{answer_chunk}\n\n{conclusion}"


@ui.page("/")  # each user/browser gets its own state here
def main_page():

    messages = ui.column().classes('w-full max-w-2xl mx-auto p-4 space-y-2')

    async def send_message():
        user_input = input_box.value.strip()
        if not user_input:
            return
        # Add user message
        with messages:
            ui.chat_message(user_input, name="You", sent=True).classes(
                "bg-blue-100 rounded-xl p-2"
            )
        input_box.value = ""

        # Get bot response
        reply = await chatbot_response(user_input)
        with messages:
            ui.chat_message(reply, name="Bot").classes(
                "bg-gray-100 rounded-xl p-2"
            )

    # Chat window
    with ui.card().classes("w-full max-w-2xl mx-auto mt-10"):
        ui.label("RAG Chatbot").classes("text-xl font-bold mb-4 text-center")
        messages  # container for chat messages

        with ui.row().classes("w-full mt-4"):
            input_box = ui.input(
                placeholder="Type a message..."
            ).props("rounded outlined dense").classes("flex-grow")

            # Trigger send on Enter
            input_box.on('keydown.enter', lambda _: asyncio.create_task(send_message()))

            ui.button("Send", on_click=send_message).props("unelevated color=blue")


ui.run(title="Chatbot", reload=False)
