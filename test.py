import gradio as gr
import random
import time
import asyncio

VALID_CODES = ["123", "1", "23", "DAPASSY"]
TIME_LIMIT = 5
START = 0
chatting = False

def toggle_visibility(is_access_granted): # this is just for going from welcome page to second
    return gr.update(visible=not is_access_granted), gr.update(visible=is_access_granted)

def start_task(): # starts the task, will start the timer
    global START, chatting
    START = time.time()
    chatting = True
    return gr.update(visible=False), gr.update(visible=True)

def end_task(): #takes them to page after the task
    return gr.update(visible=False), gr.update(visible=True)

def check_id(id_in): # checks participant id
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

async def check_time(): # having problems
    while True:
        await asyncio.sleep(1)
        if time.time() - START >= TIME_LIMIT:
            print("Time limit reached, switching pages.")
            return True


with gr.Blocks() as demo: #demo is entire app
    is_access_granted = gr.State(False)

    # need to define pages in reverse order that they show up, since the previous page will need to refer to the next page

    with gr.Row(visible=False) as end_page: # a row is an entire page, and to "change pages" you just toggle visibility
        gr.Markdown("##Please pick what you think is your (insert target here ie cretaive well written) essay from the transcript [enter the number]")

    with gr.Row(visible=False) as chat_page: #hosts the actual chatbot
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

    with gr.Row(visible=False) as start_page: #
        gr.Markdown("## Thank You For Participating, blah blah blah timer starts when you hit start task\n\n"
                    "Maybe put stuff in to double check that ID is correct"
                    "")
        start_button = gr.Button("Start Task")
        start_button.click(fn=start_task, outputs=[start_page, chat_page]) # any function to change the page you return the page itself, see toggle functions for to see how that is done with gr.update()

    with gr.Row(visible=True) as main_page: # welcome page, first page you see
        gr.Markdown("## Welcome, Please Enter Subject ID")
        password_input = gr.Textbox(label="ID Number", placeholder="ID")
        password_output = gr.Textbox(label="", interactive=False, visible=False)
        check_button = gr.Button("Continue")

        check_button.click(fn=check_id, inputs=password_input, outputs=[password_output, is_access_granted])
        check_button.click(fn=toggle_visibility, inputs=is_access_granted, outputs=[main_page, start_page])

        def show_password_output(password_output_value): # just a quick function to display if password is correct
            if password_output_value:
                return gr.update(visible=True)
            else:
                return gr.update(visible=False)

        password_output.change(fn=show_password_output, inputs=password_output, outputs=password_output)
        check_button.click(fn=toggle_visibility, inputs=is_access_granted, outputs=[main_page, start_page])

    async def monitor_time(): # It will get to the point of displaying the print statement but the update isnt working, not sure why but it has something to do with the way gradio handles updates, the only way Ive gotten
        #it to work is if your returning gr.update(visible=...) froma function that you pass to a button object so not sure how we can do that directly through the code yet
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


    demo.load(monitor_time) # loads with teh async function

demo.launch() # sends app to loaclhost usually port 7680


