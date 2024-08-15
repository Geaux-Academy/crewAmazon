import yaml
from crewai import Agent, Crew, Process, Task
import os
from amz.tools.pdf_downloader import PDFDownloader
import asyncio

def load_yaml(file_path):
    """
    Helper function to load a YAML file.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load agents and tasks configurations
agents_config = load_yaml(os.path.join(os.path.dirname(__file__), 'config/agents.yaml'))
tasks_config = load_yaml(os.path.join(os.path.dirname(__file__), 'config/tasks.yaml'))

def create_crew():
    """
    Create and configure the crew with agents and tasks.
    """
    # Create agents
    researcher = Agent(
        config=agents_config['researcher'],
        verbose=True
    )

    organizer = Agent(
        config=agents_config['organizer'],
        verbose=True
    )

    # Instantiate PDFDownloader
    pdf_downloader = PDFDownloader()

    async def download_pdfs_task():
        urls = [
            "https://www.cs.cmu.edu/~pattis/15-1XX/15-200/lectures/python.pdf",
            "https://www.csc.kth.se/utbildning/kth/kurser/DD1310/jupyter/Python.pdf"
            # Add other URLs as needed
        ]
        download_results = await pdf_downloader.download_pdfs(urls)
        return "\n".join(download_results)

    def download_pdfs_task_wrapper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(download_pdfs_task())

    # Ensure that 'agent' is not duplicated in the Task config
    research_task_config = tasks_config['research_pdfs_task'].copy()
    research_task_config['agent'] = researcher

    organize_task_config = tasks_config['organize_pdfs_task'].copy()
    organize_task_config['agent'] = organizer

    # Create tasks with the correct agent instance
    research_task = Task(
        **research_task_config
    )

    organize_task = Task(
        **organize_task_config,
        output_file='organized_pdfs_report.md'
    )

    download_pdfs_task_instance = Task(
        description="Download PDFs from the given URLs.",
        expected_output="List of downloaded PDF files.",
        execute=download_pdfs_task_wrapper,
        agent=organizer  # Assign an agent to this task
    )

    # Combine agents and tasks into a crew
    crew = Crew(
        agents=[researcher, organizer],
        tasks=[research_task, organize_task, download_pdfs_task_instance],
        process=Process.sequential,  # Execute tasks sequentially
        verbose=True
    )

    return crew
