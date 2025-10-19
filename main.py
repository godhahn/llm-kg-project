import streamlit as st
import requests
import json
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle

API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(layout="wide")
st.title("🧠 LLM-Powered Knowledge Graph Extractor")


def call_gemini(prompt, api_key):
    """Call Gemini API with a prompt and return parsed JSON response."""
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            return None, f"Error: API call failed with status code {response.status_code}. Response: {response.text}"
        
        response_json = response.json()
        model_output_string = response_json['candidates'][0]['content']['parts'][0]['text']
        
        # Strip markdown formatting
        if model_output_string.startswith("```json"):
            model_output_string = model_output_string[7:]
        if model_output_string.endswith("```"):
            model_output_string = model_output_string[:-3]
        
        return json.loads(model_output_string), None
    
    except requests.exceptions.RequestException as e:
        return None, f"Error: Network request failed. {e}"
    except json.JSONDecodeError as e:
        st.error(f"Failed to decode JSON. Raw text: {model_output_string}")
        return None, f"Error: Failed to decode JSON response from API. {e}."
    except (KeyError, IndexError) as e:
        return None, f"Error: Unexpected API response format. {e}. Response: {response_json}"


def build_step1_prompt(document_text):
    """Build prompt for Step 1: Entity extraction."""
    return f"""
    You are an AI assistant for knowledge graph extraction.
    Your task is to read the following document and perform Step 1: Entity Extraction.
    1. Identify all key entities (people, organizations, locations, events, concepts).
    2. Categorize each entity with one of: "PERSON", "ORGANIZATION", "LOCATION", "EVENT", "CONCEPT".
    3. Normalize entities.

    Your output MUST be only a JSON list of node objects with "name" and "label".

    Here is the document:
    ---
    {document_text}
    ---
    """


def build_step2_prompt(person_name, document_text):
    """Build prompt for Step 2: Personality analysis for a person."""
    return f"""
    You are an AI assistant for personality analysis.
    Analyze the personality of "{person_name}" based only on the document.

    Output MUST be a JSON object: {{"personality": "comma-separated traits"}}. If none, return empty string.

    Document:
    ---
    {document_text}
    ---
    """


def build_step3_prompt(node_names, document_text):
    """Build prompt for Step 3: Relationship extraction between entities."""
    entity_list_str = ", ".join([f'"{name}"' for name in node_names])
    return f"""
    You are an AI assistant for relationship extraction.
    Find relationships only between the following entities:
    [ {entity_list_str} ]
    Output MUST be a JSON list of edge objects with "source", "label", "target".

    Document:
    ---
    {document_text}
    ---
    """


def build_step4_prompt(document_text, generated_json_string):
    """Build prompt for Step 4: Scoring Agent for KG quality."""
    return f"""
    You are an AI Scoring Agent specializing in Knowledge Graph evaluation.
    Your task is to evaluate the quality of the "GENERATED_JSON" as an extraction from the "ORIGINAL_DOCUMENT".

    Evaluate two key metrics on a scale of 1 to 10:

    1.  **Correctness Score:**
        * Is every node, edge, and personality trait in the JSON 100% supported by the document?
        * Penalize heavily for any hallucinations, fabrications, or misinterpretations.
        * A 10/10 means zero fabricated information.

    2.  **Completeness Score:**
        * Does the JSON capture the *most important* entities, relationships, and personalities?
        * Penalize for missing key people, main events, or critical relationships mentioned.
        * A 10/10 means all key knowledge is present.

    Your output MUST be a JSON object with two keys:
    1.  `correctness_score`: An integer (1-10).
    2.  `completeness_score`: An integer (1-10).

    ---
    ORIGINAL_DOCUMENT:
    {document_text}
    ---
    GENERATED_JSON:
    {generated_json_string}
    ---

    Now, generate your evaluation JSON.
    """


def format_for_st_link_analysis(llm_json_output):
    """Convert LLM JSON output to st_link_analysis format with nodes and edges."""
    elements_nodes = []
    elements_edges = []
    node_name_to_id = {}
    node_id_counter = 1
    
    # Create nodes with unique IDs
    for node in llm_json_output.get("nodes", []):
        node_name = node.get("name")
        if not node_name or node_name in node_name_to_id:
            continue
        
        current_id = node_id_counter
        node_name_to_id[node_name] = current_id
        node_data = {
            "id": current_id,
            "label": node.get("label", "ENTITY").upper(),
            "name": node_name
        }
        
        # Add personality for person nodes
        if node_data["label"] == "PERSON":
            node_data["personality"] = node.get("personality", "")
        
        elements_nodes.append({"data": node_data})
        node_id_counter += 1
    
    # Define visual styles for different node types
    node_styles = [
        NodeStyle("PERSON", "#FF7F3E", "name", "person"),
        NodeStyle("ORGANIZATION", "#2A629A", "name", "business"),
        NodeStyle("LOCATION", "#2A629A", "name", "business"),
        NodeStyle("EVENT", "#2A629A", "name", "business"),
        NodeStyle("CONCEPT", "#2A629A", "name", "business"),
    ]
    
    # Create edges between nodes
    all_edge_labels = set()
    edge_id_counter = 1
    
    for edge in llm_json_output.get("edges", []):
        source_name = edge.get("source")
        target_name = edge.get("target")
        edge_label = edge.get("label", "RELATED_TO").upper()
        
        # Only create edges between existing nodes
        if source_name in node_name_to_id and target_name in node_name_to_id:
            elements_edges.append({
                "data": {
                    "id": f"e{edge_id_counter}",
                    "label": edge_label,
                    "source": node_name_to_id[source_name],
                    "target": node_name_to_id[target_name],
                }
            })
            all_edge_labels.add(edge_label)
            edge_id_counter += 1
    
    # Define visual styles for edges
    edge_styles = [EdgeStyle(label=label, caption="label", directed=True, color="#888888") for label in all_edge_labels]
    
    return {"nodes": elements_nodes, "edges": elements_edges}, node_styles, edge_styles


# File upload interface
uploaded_file = st.file_uploader("Upload your file", type=["txt"], label_visibility="collapsed")

if uploaded_file is not None and st.button("Extract Knowledge Graph"):
    if not API_KEY:
        st.error("Please add your GEMINI_API_KEY to st.secrets to proceed.")
    else:
        document_text = uploaded_file.getvalue().decode("utf-8")
        final_nodes = []
        final_edges = []

        # Step 1: Extract entities from document
        with st.spinner("Step 1/4: Extracting entities..."):
            step1_prompt = build_step1_prompt(document_text)
            nodes_list, error = call_gemini(step1_prompt, API_KEY)
            if error:
                st.error(f"Error in Step 1: {error}")
                st.stop()
            if not nodes_list:
                st.warning("No entities found in the document.")
                st.stop()

        # Step 2: Analyze personality for each person entity
        with st.spinner(f"Step 2/4: Analyzing personalities..."):
            for node in nodes_list:
                if node.get("label") == "PERSON":
                    step2_prompt = build_step2_prompt(node["name"], document_text)
                    personality_json, p_error = call_gemini(step2_prompt, API_KEY)
                    node["personality"] = "" if p_error else personality_json.get("personality", "")
                final_nodes.append(node)

        # Step 3: Extract relationships between entities
        with st.spinner("Step 3/4: Extracting relationships..."):
            node_names = [n["name"] for n in final_nodes]
            step3_prompt = build_step3_prompt(node_names, document_text)
            final_edges, error = call_gemini(step3_prompt, API_KEY)
            if error:
                st.error(f"Error in Step 3: {error}")
                final_edges = []
        
        # Combine nodes and edges into final structure
        llm_json_output = {"nodes": final_nodes, "edges": final_edges}

        st.markdown("---")
        
        # Step 4: Evaluate extraction quality
        with st.spinner("Step 4/4: Scoring graph quality..."):
            json_string_to_verify = json.dumps(llm_json_output, indent=2)
            step4_prompt = build_step4_prompt(document_text, json_string_to_verify)
            
            evaluation_json, v_error = call_gemini(step4_prompt, API_KEY)
            
            st.subheader("🔬 Extraction Quality Analysis")
            if v_error:
                st.warning(f"Warning: The evaluation step failed. {v_error}")
            else:
                # Display quality scores
                correctness = evaluation_json.get("correctness_score", 0)
                completeness = evaluation_json.get("completeness_score", 0)
                
                col1, col2 = st.columns(2)
                col1.metric("Correctness Score", f"{correctness}/10")
                col2.metric("Completeness Score", f"{completeness}/10")

        st.markdown("---")
        
        # Format and render the knowledge graph
        elements, node_style_objs, edge_style_objs = format_for_st_link_analysis(llm_json_output)

        st.success(f"Graph generation complete! {len(elements['nodes'])} nodes, {len(elements['edges'])} edges.")
        try:
            st_link_analysis(elements, "cose", node_style_objs, edge_style_objs, height=800)
        except Exception as e:
            st.error(f"Error rendering graph: {e}")