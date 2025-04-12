Here’s your **internal instruction document** for turning 1st-layer prompts into 2nd-layer “real scanner prompts” used during app runtime.

---

# 🧠 Instruction Document: Building 2nd-Layer Scanner Prompts from 1st-Layer Templates

## 📌 Purpose
This guide explains how to transform your **1st-layer prompt templates** (from the JSON prompt catalog) into **2nd-layer scanner prompts**, which are what your app will send to Llama 4 (on Cerebras) for real-time inference.

The idea is:
- **1st-layer prompts** are generic, reusable templates tied to vulnerability categories (e.g., SQL injection, long functions).
- **2nd-layer prompts** are **actual prompts sent to the model**, with real user code inserted and context-aware formatting applied.

---

## 🛠️ Structure of a 1st-Layer Prompt (Recap)

Each entry has:
- `language` (e.g., "Python", "SQL")
- `category` (e.g., "Security Flaws")
- `subcategory` (e.g., "SQL Injection")
- `prompt_template`: The generic instruction
- `output_format`: Expected output shape from the model

---

## 🔄 Transformation Workflow: Template ➝ Runtime Prompt

### ✅ Inputs Needed:
1. **The prompt template** from the catalog (e.g., "Analyze the following Python code for any SQL injection vulnerabilities...")
2. **The actual code snippet** (function, class, or SQL query)
3. **Optionally**: filename, file path, or line numbers for tracking

### 🧬 Output Structure:
```json
{
  "language": "Python",
  "category": "Security Flaws",
  "subcategory": "SQL Injection",
  "prompt": "[FULL 2nd-layer prompt]",
  "code_context": "[code_snippet_here]",
  "output_format": "[markdown or json, per template]",
  "source_file": "app/routes.py",
  "line_range": "123–145"
}
```

---

## 🪄 2nd-Layer Prompt Construction

### 🔧 Steps:
1. **Retrieve the prompt template** for the category.
2. **Insert the actual code snippet** into the prompt at the end as a new paragraph.
3. **Preserve output formatting expectations** from the template.
4. **Optional**: add filename/line info as a comment or context (improves LLM accuracy in some cases).

---

### 💡 Example 1: Python / SQL Injection

#### 🔹 Template (1st-layer prompt_template):
> Analyze the following Python code for any SQL injection vulnerabilities. Identify any places where untrusted input is used to construct SQL queries, explain the risk, and suggest safer alternatives (such as parameterized queries).

#### 🔹 Code Snippet:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

#### 🔹 2nd-Layer Prompt:
```
Analyze the following Python code for any SQL injection vulnerabilities. Identify any places where untrusted input is used to construct SQL queries, explain the risk, and suggest safer alternatives (such as parameterized queries).

Code:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```
```

---

### 💡 Example 2: SQL / SELECT * Detection

#### 🔹 Template:
> Analyze the SQL query for use of SELECT *. If the query selects all columns using SELECT *, explain why this can be inefficient or problematic (for performance and maintainability) and suggest selecting only needed columns instead.

#### 🔹 Code:
```sql
SELECT * FROM orders WHERE status = 'completed';
```

#### 🔹 2nd-Layer Prompt:
```
Analyze the SQL query for use of SELECT *. If the query selects all columns using SELECT *, explain why this can be inefficient or problematic (for performance and maintainability) and suggest selecting only needed columns instead.

SQL Query:
SELECT * FROM orders WHERE status = 'completed';
```

---

## 🧩 Integration Flow (in-app)

```mermaid
graph TD
    A[Input Python/SQL file] --> B[Break into scan targets: functions, blocks, queries]
    B --> C[Select applicable 1st-layer prompts by language & category]
    C --> D[Insert code into prompt_template ➝ 2nd-layer prompt]
    D --> E[Send to Cerebras (Llama 4 inference)]
    E --> F[Parse model response according to `output_format`]
    F --> G[Store results with code metadata for UI/reporting]
```

---

## 🧠 Best Practices

- 🔄 Always sanitize and truncate large code blocks to fit token limits.
- 📊 Group related prompts into **multi-round batches** (e.g., security scan phase, performance scan phase).
- 📁 Include source file and line context in metadata to tie findings back to the codebase.
- ⚙️ Use output_format to parse model responses automatically (markdown bullets, structured JSON, etc.).
- 🗂️ Organize all 2nd-layer prompts and results under a scanning session object (for tracking and deduplication).

---

## ✅ Optional Enhancements

- **Confidence Rating**: Add a follow-up prompt asking Llama 4 to rate its confidence per issue (helps reduce false positives).
- **Explanation Booster**: Run a second prompt like:  
  > “Please elaborate on the reasoning for each issue found in the previous analysis.”

- **Autofix Prototype (Advanced)**:  
  For very specific issues (e.g., “SELECT *”), ask the model:
  > “Can you rewrite this query using only the necessary columns?”

---

## 🧪 Testing Tips
- Feed in **known-vulnerable snippets** to validate each category prompt.
- Verify parsing logic handles markdown vs JSON cleanly.
- Monitor token usage — break down large functions where needed.

---
