import gradio as gr

from sources.research import query_research

def query(message, history):
    answer = query_research(message)
    return answer
demo = gr.ChatInterface(
    query, 
    input=image,
    textbox=gr.Textbox(placeholder="Ask me a question about Subspace"),
)

demo.launch()

# prompt templating -> ask user for version of subspace 