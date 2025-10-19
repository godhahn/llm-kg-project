# LLM-Powered Knowledge Graph Extractor

## Project Overview

This **Streamlit web** application automatically extracts structured knowledge from unstructured text documents and visualizes it as an **interactive knowledge graph**. Powered by **Google's Gemini LLM**, the app uses a multi-step AI pipeline to identify entities, relationships, and even personality traits of individuals mentioned in the text.

The application is ideal for researchers, analysts, or anyone who wants to **convert raw text into clear, visual insights** through knowledge graph exploration.

- For the full LLM reasoning and interaction used for this project:
[Shared LLM Session](https://gemini.google.com/share/794002dc6157)
- For a deeper dive into design choices, insights, and limitations:  [Report](REPORT.md)

## Features

- Upload `.txt` files to automatically generate a knowledge graph.
- 4-step LLM pipeline:
    1. Entity Extraction – Detects people, organizations, locations, events, and concepts.
    2. Personality Analysis – Assigns personality traits to `PERSON` nodes.
    3. Relationship Extraction – Identifies connections between entities.
    4. Graph Quality Scoring – Evaluates correctness and completeness of the graph.
- Interactive Visualization – Explore the knowledge graph using `st_link_analysis`.

## Repository Contents

- `assets/`: Sample documents for testing and demo purposes.
- `main.py`: Complete Streamlit application source code.

## Getting Started

### Step 1: Clone Repository and Install Dependencies

```bash
git clone <repo_url>
cd <repo_name>
pip install streamlit requests st-link-analysis
```

### Step 2: Configure API Key
Create `.streamlit/secrets.toml` with your Gemini API key:
```bash
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

### Step 3: Run the Application
```bash
streamlit run main.py
```
Open your browser and navigate to the provided Streamlit URL.


Upload a `.txt` file and click **"Extract Knowledge Graph"** to begin.
