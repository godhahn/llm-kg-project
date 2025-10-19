# Report: Design Choices, Insights, and Limitations

## 1. Synthetic Data Generation

Approach:

To test the pipeline without a real dataset, synthetic data was generated. The target knowledge graph (KG) was defined as a structured JSON object with nodes, edges, and personality traits. This JSON was then used by an LLM to generate coherent 500-word narratives that naturally incorporated all facts. Sample files are available in `assets/`.

Justification:

- Guaranteed Ground Truth: Ensures evaluation against fully accurate references.
- Controlled Complexity: Allows testing of varying graph densities to stress-test the pipeline.

## 2. Model Evaluation and Metrics

Approach:

- A "Scoring Agent" LLM evaluates the final KG against the text. Key metrics include:
    - Correctness: Measures factual accuracy and penalizes hallucinations.
    - Completeness: Measures coverage of relevant entities and relationships.

Justification:

- Semantic Nuance: LLMs can recognize equivalence beyond literal strings.
- Industry Precedent: LLMs as evaluators are commonly used in AI benchmarking.

## 3. Implementation and Personality Representation

Approach:

- Streamlit app (`main.py`) for interactive visualization.
- Gemini LLM used for entity extraction, relationship detection, and personality analysis.
- KG Representation:
    - Node: Entity (with optional personality traits for `PERSON` nodes)
    - Edge: Relationship between nodes
    - Personality traits displayed on click for clean, intuitive exploration.

Justification:

- Streamlit: Rapid development of interactive apps with minimal code.
- Gemini LLM: Strong reasoning and entity/personality extraction capabilities.
- Node/Edge labeling and on-click personality display improve clarity and usability.

## 4. LLM Workflow Pipeline

Approach: 4-step sequential pipeline:

1. Entity Extraction: Identify and normalize nodes.
2. Personality Analysis: Assign personality traits to `PERSON` nodes.
3. Relationship Extraction: Identify edges between confirmed nodes.
4. Quality Scoring: Evaluate the graph against the source text.

Justification:

- Chain-of-Prompts: Stepwise reasoning reduces cognitive load.
- Reduces Hallucinations: Later steps use outputs from previous steps for context.
- Debugging Friendly: Easier to locate and fix errors.
- Mimics Advanced Reasoning: Similar to chain-of-thought prompting in LLMs.

## 5. Data Processing and Normalization

Approach:

- Entities normalized to deduplicate mentions.
- Relationships left unnormalized to preserve semantic nuance.

Justification:

- Entity Normalization: Prevents fragmentation and ensures accuracy.
- Preserving Relationships: Maintains fidelity to the source text.

## 6. Limitations

- LLM Reliability: Occasional misinterpretations or hallucinations may occur.
- Graph Representation: Structured triples cannot capture all textual nuance.
- Input Restrictions: Limited to `.txt` files; large documents may require chunking.