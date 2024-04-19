import sys
import time
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
import os
import re
from pydantic.v1 import BaseModel, Field
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
)
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
import urllib
import hashlib

# NOTE: to find which model names you have, use cli tool:  `ollama list`
# llm = ChatOpenAI(
#       model='llama2',
#       base_url="http://localhost:11434/v1",
#       api_key="NA"
#     )

llm = ChatOpenAI(model="gpt-4-turbo", verbose=True)


# to keep track of tasks performed by agents
task_values = []


scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")

# create the directory for the scripts
if not os.path.exists(scripts_dir):
    os.makedirs(scripts_dir)

class SimpleDoc(BaseModel):
    text: str = Field(title="Text", description="The text to save, in Markdown format")


# make sure it exists
if not os.path.exists(scripts_dir):
    os.makedirs(scripts_dir)


def create_crewai_setup(
    movie_slug, movie_name, movie_genre="Action", movie_visual_style="Cartoon", movie_idea="A heist movie"
):

    # make sure the movie_slug directory exists in scripts_dir
    movie_dir = os.path.join(scripts_dir, movie_slug)

    print("movie_dir", movie_dir)

    # ensure that movie_dir exists
    if not os.path.exists(movie_dir):
        os.makedirs(movie_dir)

    # write an initial idea into f"{movie_dir}/idea_original.md"
    with open(f"{movie_dir}/idea_original.md", "w") as f:
        f.write(
            f"""# {movie_name}
Genre: {movie_genre}

## Plot
{movie_idea}
"""
        )

    docs_tool = DirectoryReadTool(directory=movie_dir)
    file_tool = FileReadTool()

    def run_and_store_image(description):
        # Run the image generator and get the returned URL
        original_url = DallEAPIWrapper(size="1792x1024", quality="hd", model="dall-e-3").run(description)

        # Store the file locally
        image_path = os.path.join(movie_dir, f"image_{hashlib.md5(original_url.encode()).hexdigest()}.png")
        urllib.request.urlretrieve(original_url, image_path)

        # Return the local URL as a relative path
        return image_path

    image_generator_tool = Tool(
        "Dall-E-Image-Generator",
        run_and_store_image,
        "The OpenAI DALL-E API. Useful for when you need to generate images from a text description. Input should be an image description.",
    )

    # Define Agents
    screenwriter = Agent(
        role="Screenwriter",
        goal=f"""Establish the premise, setting and write the dialog for {movie_name}, and integrate any feedback. You run the writers room and debate the best way to approproach the story.""",
        backstory=f"""Your name is Daniel Walmsley. You are the writer for "{movie_name}". You are a master in the {movie_genre} genre. Your inspirations are Shakespeare and Quentin Tarantino.""",
        verbose=True,
        allow_delegation=True,
        tools=[
            docs_tool,
            file_tool,
        ],
        llm=llm,
    )

    cinematographer = Agent(
        role="Cinematographer",
        goal=f"""Create a visual style for {movie_name} based on the treatment provided by the screenwriter. You will be responsible for the look and feel of the movie.""",
        backstory=f"""You are the cinematographer for "{movie_name}". Your inspirations are Roger Deakins and Emmanuel Lubezki.""",
        verbose=True,
        allow_delegation=True,
        tools=[
            docs_tool,
            file_tool,
        ],
        llm=llm,
    )

    script_consultant = Agent(
        role="Script Consultant",
        goal=f"""Provide feedback on the script for {movie_name} and suggest improvements.""",
        backstory=f"""You are a script consultant for "{movie_name}". Your inspirations are Nora Ephron and David Mamet.""",
        verbose=True,
        allow_delegation=True,
        tools=[
            docs_tool,
            file_tool,
        ],
        llm=llm,
    )

    writer = Agent(
        role="Writer",
        goal=f"""Write the dialog for {movie_name} based on the outline provided by the screenwriter. You will also be responsible for integrating any feedback.""",
        backstory=f"""You are a writer for "{movie_name}". Your inspirations are J.K. Rowling and Aaron Sorkin.""",
        verbose=True,
        allow_delegation=False,
        tools=[
            docs_tool,
            file_tool,
        ],
        llm=llm,
    )

    director = Agent(
        role="Director",
        goal=f"""Turn the script for "{movie_name}" into storyboards, and plan the shots and angles for the film. You will also be responsible for casting and overseeing the production.""",
        backstory=f"""You are the director for "{movie_name}". Your inspirations are Steven Spielberg and Alfred Hitchcock.""",
        verbose=True,
        allow_delegation=True,
        tools=[
            docs_tool,
            file_tool,
        ],
        llm=llm,
    )

    producer = Agent(
        role="Producer",
        goal=f"""Ensure that "{movie_name}" has all the elements it needs to be successful, including marketing materials and product placement.""",
        backstory=f"""You are the producer for "{movie_name}". Your inspirations are Jerry Bruckheimer and Kathleen Kennedy.""",
        verbose=True,
        allow_delegation=True,
        llm=llm,
        tools=[
            docs_tool,
            file_tool,
        ],
    )

    # Define Tasks
    define_plot = Task(
        description=f"""Establish the plot, setting, and characters for {movie_name}, in the {movie_genre} genre. In brief, the main idea is: {movie_idea}.""",
        expected_output="A one-pager with the title, subtitle (if any), plot, setting, and characters for the movie. Ask the script consultant for any feedback and integrate it into your work.",
        agent=screenwriter,
        output_file=f"{movie_dir}/idea_draft.md",
    )

    write_treatment = Task(
        description=f"""\
            Write a treatment for {movie_name} based on the plot, setting, and characters in the {movie_genre} genre based on the file {movie_dir}/idea_draft.md.
            Consult with the script consultant and writer to integrate any feedback. Be sure it remains true to the original idea: {movie_idea}
        """,
        expected_output="A concise treatment for the movie, no more than 10 pages, including title, logline, characters and synopsis. Also be sure to include a detailed description of the art style, color scheme, etc.",
        agent=screenwriter,
        output_file=f"{movie_dir}/treatment.md",
        context=[define_plot],
    )

    # director_review_treatment = Task(
    #     description=f"""Review the treatment for {movie_name} and provide feedback based on the file in {movie_dir}/treatment_draft.md. Ensure that the movie will be cinematic, moving, funny and suspenseful.""",
    #     expected_output="Feedback on the treatment for the movie.",
    #     agent=director,
    #     output_file=f"{movie_dir}/treatment_review.md",
    #     context=[write_treatment],
    # )

    # treatment_final = Task(
    #     description=f"""Finalize the treatment for {movie_name} based on the feedback in the file {movie_dir}/treatment_review.md. Ensure that the movie will be cinematic, moving, funny and suspenseful.""",
    #     expected_output="The final treatment for the movie.",
    #     agent=screenwriter,
    #     output_file=f"{movie_dir}/treatment_final.md",
    #     context=[write_treatment, director_review_treatment],
    # )

    write_lookbook = Task(
        description=f"""Create a lookbook for the visual style of {movie_name} based on the treatment in the file {movie_dir}/treatment.md. Include images, color schemes, art style, and any other visual references that will help the cinematographer and director. In place of actual illustrations include extremely detailed visual descriptions. Be sure to include the visual style - e.g. cartoon, 3d animation, live action, etc.""",
        expected_output="A lookbook for the visual style of the movie.",
        agent=cinematographer,
        output_file=f"{movie_dir}/lookbook.md",
        context=[write_treatment],
    )

    def write_script_act(movie_name, movie_dir, act_description, act_file, agent, context=[]):
        return Task(
            description=f"""Write the {act_description} script for {movie_name} based on the treatment in the file {movie_dir}/treatment.md, in the {movie_genre} genre. Consult with the screenwriter, script consultant, and director to integrate any feedback.""",
            expected_output=f"The complete {act_description} of the movie script.",
            agent=agent,
            output_file=f"{movie_dir}/{act_file}",
            context=context,
        )

    write_first_act = write_script_act(
        movie_name,
        movie_dir,
        "first act",
        "first_act_draft.md",
        screenwriter,
        context=[write_treatment],
    )

    write_second_act = write_script_act(
        movie_name,
        movie_dir,
        "second act",
        "second_act_draft.md",
        screenwriter,
        context=[write_treatment, write_first_act],
    )

    write_third_act = write_script_act(
        movie_name,
        movie_dir,
        "third act",
        "third_act_draft.md",
        screenwriter,
        context=[write_treatment, write_first_act, write_second_act],
    )

    def create_storyboard_task(movie_name, movie_dir, act_description, storyboard_file, context=[]):
        return Task(
            description=f"""Create a storyboard for the {act_description} of {movie_name} based on the {act_description}. Descrbe each scene on its own paragraph, as if describing the frames on the storyboard. Make the descriptions rich enough for our artists to paint the scenes, with angle, pose, and detailed character information.""",
            expected_output=f"Storyboard for the {act_description} of the movie.",
            agent=director,
            output_file=f"{movie_dir}/{storyboard_file}",
            context=context,
        )

    storyboard_first_act = create_storyboard_task(
        movie_name,
        movie_dir,
        "first act",
        "first_act_storyboard_draft.md",
        context=[write_first_act],
    )

    storyboard_second_act = create_storyboard_task(
        movie_name,
        movie_dir,
        "second act",
        "second_act_storyboard_draft.md",
        context=[write_second_act, storyboard_first_act],
    )

    storyboard_third_act = create_storyboard_task(
        movie_name,
        movie_dir,
        "third act",
        "third_act_storyboard_draft.md",
        context=[write_third_act, storyboard_first_act, storyboard_second_act],
    )

    def illustrate_storyboard_task(movie_name, movie_dir, act_description, storyboard_file, illustration_file, context=[]):
        return Task(
            description=f"""Create an illustrated storyboard for the {act_description} of {movie_name} based on the storyboard in {storyboard_file}.
            Also consult the overview of the movie in idea_draft.md and the lookbook in lookbook.md.
            Include a detailed description of the visual style and each character that is as consistent as possible, giving the world a consistent tone, color palette, and style across illustrations.
            If a character is old, young, tall, short, has a certain hair or clothing style, then specify that in the description.
            Always include specific tonal prompts like "pixar, 3d animated, cartoon" or "realistic, gritty, 2d animated, realistic" to help guide the artists.
            Include specific framing details like "from above" or "close-up".
            Always include character descriptions, like "long brown hair, pale skin, pointed nose", etc, with every generated image.
            Clearly describe what is in the foreground, what is in the background, and any costumers or other details that are important.
            Clearly describe the relationship between the characters, for example whether one is pointing at another, or one is looking at another, or standing in front or behind the other.
            Include an image for every scene in the storyboard. Do not skip any images.
            YOU MUST FEED THE ENTIRE DESCRIPTION INTO THE DALL-E TOOL. DO NOT SKIP ANY DETAILS.
            Use the Dall-E tool whenever you need to create an image and provide all the details I specified in the image description.
            Use the URL returned by Dall-E EXACTLY as it is, and do not modify it in any way. Keep all the query parameters intact.""",
            expected_output=f"Storyboard for the {act_description} of the movie in markdown format with shot title, description and full embedded image URL. Do NOT wrap it in a code block, and ALWAYS include the full image URL.",
            agent=director,
            tools=[docs_tool, file_tool, image_generator_tool],
            output_file=f"{movie_dir}/{illustration_file}",
            context=context,
        )

    illustrate_first_act_storyboard = illustrate_storyboard_task(
        movie_name,
        movie_dir,
        "first act",
        "first_act_storyboard_draft.md",
        "first_act_illustration.md",
        context=[write_treatment, write_lookbook, storyboard_first_act],
    )

    illustrate_second_act_storyboard = illustrate_storyboard_task(
        movie_name,
        movie_dir,
        "second act",
        "second_act_storyboard_draft.md",
        "second_act_illustration.md",
        context=[write_treatment, write_lookbook, storyboard_second_act],
    )

    illustrate_third_act_storyboard = illustrate_storyboard_task(
        movie_name,
        movie_dir,
        "third act",
        "third_act_storyboard_draft.md",
        "third_act_illustration.md",
        context=[write_treatment, write_lookbook, storyboard_third_act],
    )

    # Create and Run the Crew
    product_crew = Crew(
        agents=[screenwriter, director, producer, writer, script_consultant],
        tasks=[
            define_plot,
            write_treatment,
            # director_review_treatment,
            # treatment_final,
            write_lookbook,
            write_first_act,
            write_second_act,
            write_third_act,
            storyboard_first_act,
            storyboard_second_act,
            storyboard_third_act,
            illustrate_first_act_storyboard,
            illustrate_second_act_storyboard,
            illustrate_third_act_storyboard,
        ],
        verbose=2,
        process=Process.sequential,
    )

    crew_result = product_crew.kickoff()
    return crew_result


# display the console processing on streamlit UI
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ["red", "green", "blue", "orange"]  # Define a list of colors
        self.color_index = 0  # Initialize color index

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r"\x1B\[[0-9;]*[mK]", "", data)

        # Check if the data contains 'task' information
        task_match_object = re.search(
            r"\"task\"\s*:\s*\"(.*?)\"", cleaned_data, re.IGNORECASE
        )
        task_match_input = re.search(
            r"task\s*:\s*([^\n]*)", cleaned_data, re.IGNORECASE
        )
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(
                self.colors
            )  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace(
                "Entering new CrewAgentExecutor chain",
                f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]",
            )

        if "Producer" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Producer", f":{self.colors[self.color_index]}[Producer]"
            )

        if "Director" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Director", f":{self.colors[self.color_index]}[Director]"
            )

        if "Screenwriter" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Screenwriter", f":{self.colors[self.color_index]}[Screenwriter]"
            )

        if "Script Consultant" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Script Consultant",
                f":{self.colors[self.color_index]}[Script Consultant]",
            )

        if "Writer" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Writer", f":{self.colors[self.color_index]}[Writer]"
            )

        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]"
            )

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown("".join(self.buffer), unsafe_allow_html=True)
            self.buffer = []


# Streamlit interface
def run_crewai_app():
    st.title("Let's Write a Movie")

    movie_slug = st.text_input(
        "Movie Slug, e.g. 'the_heist' - used for file naming", "little_bean"
    )

    movie_name = st.text_input(
        "Movie Name, e.g. 'The Heist'", "The Little Bean and Tiger go Rogue!"
    )

    movie_genre = st.selectbox(
        "Select the genre of the movie", ["Action", "Comedy", "Drama", "Sci-Fi"], 1
    )

    movie_visual_style = st.selectbox(
        "Select the visual style of the movie",
        ["Realistic", "Cartoon", "Anime", "Pixar", "Gritty"],
        1,
    )

    movie_idea = st.text_area(
        "Enter a brief idea for the movie",
        "A hilarious childrens animated adventure about Little Bean (real name: Lola), a neurotic little white chihuaha/something cross, and Tiger, a brave ginger cat. Together they have to get to Nevada City to save their owner Indigo from a math-related disaster...",
    )

    if st.button("Write Movie"):
        # Placeholder for stopwatch
        stopwatch_placeholder = st.empty()

        # Start the stopwatch
        start_time = time.time()
        with st.expander("Processing!"):
            sys.stdout = StreamToExpander(st)
            with st.spinner("Generating Results"):
                crew_result = create_crewai_setup(
                    movie_slug, movie_name, movie_genre, movie_visual_style, movie_idea
                )

        # Stop the stopwatch
        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Total Time Elapsed: {total_time:.2f} seconds")

        st.header("Tasks:")
        st.table({"Tasks": task_values})

        st.header("Results:")
        st.markdown(crew_result)


if __name__ == "__main__":
    run_crewai_app()
