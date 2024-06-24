import gradio as gr
import random
import time
import asyncio

VALID_CODES = ["123", "1", "23", "DAPASSY"]
TIME_LIMIT = 5
START = 0
chatting = False

def toggle_visibility(is_access_granted):
    return gr.update(visible=not is_access_granted), gr.update(visible=is_access_granted)

def start_task():
    global START, chatting
    START = time.time()
    chatting = True
    return gr.update(visible=False), gr.update(visible=True)

def end_task():
    return gr.update(visible=False), gr.update(visible=True)

def check_id(id_in):
    if id_in in VALID_CODES:
        return f"Welcome Participant {id_in}", True
    else:
        return "Not a valid Subject ID", False

def respond(message, chat_history): #Generic response function
    bot_message = (random.choice(["How are you?", "I love you", "I'm very hungry"]) + " Elapsed: " + str(time.time() - START) + " Chatting: " + str(chatting)
                   + " Over Time Limit: " + str(time.time() - START >= TIME_LIMIT and chatting)
)
    chat_history.append((message, bot_message))
    time.sleep(.2)
    return "", chat_history

async def check_time():
    while True:
        await asyncio.sleep(1)
        if time.time() - START >= TIME_LIMIT:
            print("Time limit reached, switching pages.")
            return True


with gr.Blocks() as demo: #demo is entire app
    is_access_granted = gr.State(False)

    with gr.Row(visible=False) as end_page:
        gr.Markdown("##Please pick what you think is your (insert target here ie cretaive well written) essay from the transcript [enter the number]")

    with gr.Row(visible=False) as chat_page:
        if time.time() - START >= TIME_LIMIT and chatting:
            print("trying to change, conrtol is working")
            chat_page = gr.update(visible=False)
            end_page = gr.update(visible=True)

        print("Message Went ")
        chatbot = gr.Chatbot(min_width=900, height=600)
        msg = gr.Textbox(min_width=900)
        msg.submit(fn=respond, inputs=[msg, chatbot], outputs=[msg, chatbot])

        # else:
            # chatbot = gr.Chatbot(min_width=900, height=600)
            # msg = gr.Textbox(min_width=900)
            # msg.submit(respond, [msg, chatbot], [msg, chatbot])

    with gr.Row(visible=False) as start_page:
        gr.Markdown("## Thank You For Participating, blah blah blah timer starts when you hit start task\n\n"
                    "Maybe put stuff in to double check that ID is correct"
                    "")
        start_button = gr.Button("Start Task")
        start_button.click(fn=start_task, outputs=[start_page, chat_page])

    with gr.Row(visible=True) as main_page:
        gr.Markdown("## Welcome, Please Enter Subject ID")
        password_input = gr.Textbox(label="ID Number", placeholder="ID")
        password_output = gr.Textbox(label="", interactive=False, visible=False)
        check_button = gr.Button("Continue")

        check_button.click(fn=check_id, inputs=password_input, outputs=[password_output, is_access_granted])
        check_button.click(fn=toggle_visibility, inputs=is_access_granted, outputs=[main_page, start_page])

        def show_password_output(password_output_value):
            if password_output_value:
                return gr.update(visible=True)
            else:
                return gr.update(visible=False)

        password_output.change(fn=show_password_output, inputs=password_output, outputs=password_output)
        check_button.click(fn=toggle_visibility, inputs=is_access_granted, outputs=[main_page, start_page])

    async def monitor_time():
        global main_page, start_page, chat_page, end_page
        while True:
            await asyncio.sleep(1)
            if await check_time():
                print("Trying to switch")
                # time_up.value = True
                main_page = gr.update(visible=False)
                start_page = gr.update(visible=False)
                chat_page = gr.update(visible=False)
                end_page = gr.update(visible=True)


    demo.load(monitor_time)

demo.launch()


