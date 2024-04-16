# Douglas Story Generator

This is an experiment is using CrewAI to write the scripts and storyboards for a movie based on a brief description.

It's named for my favourite author, Douglas Adams.

It produces the following files in `scripts/movie_slug/` where `movie_slug` is the slugified version of the movie title:

The idea:

 * idea_original.md
 * idea_draft.md

The treatment:

 * treatment_draft.md
 * treatment_review.md
 * treatment_final.md

The script:

 * first_act_draft.md
 * second_act_draft.md
 * third_act_draft.md

The storyboard:

 * first_act_storyboard_draft.md
 * second_act_storyboard_draft.md
 * third_act_storyboard_draft.md

The illustrations:

 * first_act_illustration.md
 * second_act_illustration.md
 * third_act_illustration.md

### Prerequisites

Before proceeding, ensure you have the following installed on your system:

- Python (version 3.10 or higher)
- pip (Python package installer)

It's recommended to use a virtual environment like conda or micromamba. I prefer micromamba, but you can use conda if you prefer.

e.g.

```bash
micromamba create -c conda-forge -n douglas python==3.10
micromamba activate douglas
```

### Installation Steps

1. **Clone the Repository:**

   Clone the project repository to your local machine using Git by running the following command in your terminal or command prompt:

   ```
   git clone https://github.com/gravityrail/douglas.git
   ```

2. **Navigate to Project Directory:**

   Change your working directory to the project directory using the following command:

   ```
   cd douglas
   ```

3. **Install Dependencies:**

   Install the required Python dependencies listed in the `requirements.txt` file using pip. Run the following command:

   ```
   pip install -r requirements.txt
   ```
4. **Set Up OpenAI API Key:**

   To utilize the OpenAI API within the application, ensure you have an OpenAI API key. Set your OpenAI API key as an environmental variable named OPENAI_API_KEY on your system. Replace sk-xxxxxxxxxxxxxxxxx with your actual OpenAI API key.

   ```
   export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
   ```

   OR

   Create a .env file in the project directory if it doesn't exist already. Add the following line to the .env file, replacing sk-xxxxxxxxxxxxxxxxx with your actual OpenAI API key:

   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
   ```

### Running the Streamlit Application

Once you've completed the setup steps, you can run the Streamlit application using the following command:

```
streamlit run main.py
```

This command will launch the application, and you should see the URL where the app is running. Typically, it will be something like `http://localhost:8501`.

### Usage

- Upon running the Streamlit application, you will be presented with the interface of the CrewAI Movie Writers.

### Credit

This repo was stolen directly from https://github.com/AbubakrChan/crewai-business-product-launch, which was a super helpful starting point for someone who has never used Streamlit before.