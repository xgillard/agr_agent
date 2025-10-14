from langchain_core.runnables.graph import MermaidDrawMethod

from agents.local_llm.agatha.graph import ask_agatha_graph

ask_agatha_graph().get_graph(xray=True).draw_mermaid_png(
    output_file_path="agent.png",
    draw_method=MermaidDrawMethod.PYPPETEER,
)