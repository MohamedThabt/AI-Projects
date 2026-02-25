import gradio as gr


def create_project1_page() -> tuple[gr.Column, gr.Button]:
    """Build the Project 1 page and return (column, back_button)."""
    with gr.Column(visible=False) as project1_page:
        gr.Markdown("## Project 1")
        gr.Markdown("Welcome to Project 1!")
        back_btn = gr.Button("← Back to Home", variant="secondary")

    return project1_page, back_btn
