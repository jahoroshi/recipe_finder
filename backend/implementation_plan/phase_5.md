Я обновлю Phase 5, добавив паттерн Judge для валидации результатов поиска:

## Phase 5: LangGraph Workflows (Updated)

### 5.2 Search Pipeline Workflow with Judge Pattern

**Graph Structure:**
```python
SearchPipelineGraph:
    START -> parse_query
    parse_query -> generate_embedding [conditional]
    parse_query -> extract_filters [conditional]
    generate_embedding -> vector_search
    extract_filters -> filter_search
    vector_search -> merge_results
    filter_search -> merge_results
    merge_results -> judge_relevance  # NEW NODE
    judge_relevance -> rerank [conditional]
    rerank -> format_response
    format_response -> END
```

**Updated Node Implementations:**

### Judge Relevance Node (New)
**Purpose:** Validate search results against original query parameters and filter out items that don't meet configurable relevance thresholds.

**Key Responsibilities:**
- Evaluate each result against search criteria using configurable metrics
- Score results based on multiple relevance dimensions (ingredient match, cuisine accuracy, dietary compliance, etc.)
- Apply configurable thresholds to filter low-relevance results
- Generate relevance reports for monitoring and optimization
- Support different judge strategies based on query type

**Configurable Metrics:**
- **Semantic similarity threshold**: Minimum cosine similarity score for vector search results
- **Filter compliance score**: Percentage of matched vs requested filters
- **Ingredient match ratio**: For ingredient-based searches
- **Dietary restriction adherence**: Strict validation for dietary requirements
- **Confidence threshold**: Minimum confidence score for keeping results
- **Result count limits**: Min/max results to pass through

**Judge Configuration Schema:**
```
JudgeConfig:
    - semantic_threshold: float (0.0-1.0)
    - filter_compliance_min: float (0.0-1.0)
    - ingredient_match_min: float (0.0-1.0)
    - dietary_strict_mode: boolean
    - confidence_threshold: float (0.0-1.0)
    - min_results: int
    - max_results: int
    - fallback_strategy: enum (RELAX_THRESHOLDS, EMPTY_RESULTS, SUGGEST_ALTERNATIVES)
```

**Integration Points:**
- Receives merged results from both vector and filter searches
- Access to original query parameters for validation
- Can trigger re-ranking if significant filtering occurs
- Logs filtering decisions for analysis and metric tuning

### 5.3 Workflow State Management (Updated)

**Enhanced SearchPipelineState:**
```python
class SearchPipelineState(TypedDict):
    query: str
    parsed_query: Dict[str, Any]
    filters: Dict[str, Any]
    embedding: Optional[List[float]]
    vector_results: List[Recipe]
    filter_results: List[Recipe]
    merged_results: List[Recipe]
    judge_metrics: Dict[str, float]  
    filtered_results: List[Recipe]    
    judge_report: Dict[str, Any]      
    final_results: List[Recipe]
    metadata: Dict[str, Any]
```

The judge node ensures search quality by validating that results truly match user intent, with metrics that can be tuned based on user feedback and search performance analytics.


# Post-Implementation Tasks

### 1. Write unit tests AND RUN created tests(!!!)
Verify implemented workflow functionality:
- RecipeProcessingGraph node execution and state transitions
- SearchPipelineGraph parallel execution and result merging
- Workflow state management and error handling
- Node implementations (validation, embedding, search, etc.)

### 2. Update Claude.md
Add to documentation:
- Implemented workflow graphs and their structure
- Node implementations and responsibilities
- State management schemas
- Workflow execution flow and error handling


---