from flask import Flask, render_template, request, jsonify
from langchain_community.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
import os
import re
import datetime

app = Flask(__name__)

# Set your API keys
os.environ["SERPAPI_API_KEY"] = "b6f655a92e5ddc1175d64f16fb60ffa41dbde1bb50b21c4c8c09ae34e43e83f5"
os.environ["OPENAI_API_KEY"] = "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"

search = SerpAPIWrapper(serpapi_api_key=os.environ["SERPAPI_API_KEY"])
tools = [Tool(
    name="Google Search",
    func=search.run,
    description=(
        "Search the web. To answer the user's question, combine and synthesize information from multiple up-to-date, reliable sources. "
        "For each key fact or claim, add a citation in the form [source1], [source2], etc. "
        "At the end of your answer, provide a list of the sources with their URLs, matching the citation tags. "
        "Always use the most recent and up-to-date sources available. "
        f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}. "
    )
)]

llm = ChatOpenAI(model_name="gpt-4.1", temperature=0)
agent = initialize_agent(
    tools=tools,    
    llm=llm,
    agent="zero-shot-react-description",
    verbose=False,
    handle_parsing_errors=True
)

def format_result_to_html(result):
    if isinstance(result, dict) and 'output' in result:
        result = result['output']
    lines = [line.strip() for line in result.split('\n') if line.strip()]
    html_lines = []
    current_item = []
    for line in lines:
        if re.match(r'^\d+\.', line):
            if current_item:
                html_lines.append(current_item)
            current_item = [line]
        else:
            if current_item:
                current_item.append(line)
    if current_item:
        html_lines.append(current_item)

    html = ['<ol>']
    for item in html_lines:
        # First line is the title
        title_line = item[0]
        title = re.sub(r'^\d+\.\s*', '', title_line)
        url = None
        description_lines = []
        for l in item[1:]:
            # Look for a line like "- Source: https://..."
            source_match = re.search(r'(https?://[^\s]+)', l)
            if source_match:
                url = source_match.group(1)
            else:
                description_lines.append(l)
        # Make the title a clickable link if URL exists
        if url:
            title_html = f'<a href="{url}" target="_blank">{title}</a>'
        else:
            title_html = title
        description_html = '<br>'.join(description_lines)
        html.append(f'<li>{title_html}<br>{description_html}</li>')
    html.append('</ol>')
    return '\n'.join(html)

def parse_results(result):
    if isinstance(result, dict) and 'output' in result:
        result = result['output']
    lines = [line.strip() for line in result.split('\n') if line.strip()]
    results = []
    current = None
    for line in lines:
        # Start of a new result
        m = re.match(r'^(\d+)\.\s*(.*)', line)
        if m:
            if current:
                results.append(current)
            current = {'title': m.group(2), 'description': '', 'score': None, 'reliability': None, 'url': None, 'date': None}
        elif current is not None:
            # Relevance Score
            if 'Relevance Score:' in line:
                score_match = re.search(r'([0-9.]+)', line)
                if score_match:
                    current['score'] = float(score_match.group(1))
            # Reliability Score
            elif 'Reliability Score:' in line:
                rel_match = re.search(r'([0-9.]+)', line)
                if rel_match:
                    current['reliability'] = float(rel_match.group(1))
            # Date
            elif re.search(r'(20\d{2}(-\d{2}-\d{2})?)', line) or re.search(r'(20\d{2})', line):
                date_match = re.search(r'(20\d{2}(-\d{2}-\d{2})?)', line)
                if date_match:
                    current['date'] = date_match.group(1)
            # URL
            elif 'Source:' in line or 'URL:' in line:
                url_match = re.search(r'(https?://[^\s]+)', line)
                if url_match:
                    current['url'] = url_match.group(1)
            # Description
            else:
                current['description'] += (line + ' ')
    if current:
        results.append(current)
    return results

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search_query():
    data = request.get_json()
    query = data.get("query", "")

    prompt = query
    try:
        result = agent.invoke({"input": prompt})
        if isinstance(result, dict) and 'output' in result:
            result = result['output']
        # given the result, insert them into another AI to generate a list of tasks
        model = ChatOpenAI(model_name="gpt-4.1", temperature=0.5)
        prompt = (
            f"Given the following result: {result}\n"
            "Generate up to 3 actionable web-based tasks the user may want to take based on the answer. "
            "Output ONLY the tasks as a numbered list (1., 2., 3.) with no introduction or explanation."
        )
        task_result = model.invoke(prompt)
        if hasattr(task_result, 'content'):
            task_result = task_result.content
        elif isinstance(task_result, dict) and 'output' in task_result:
            task_result = task_result['output']
        return jsonify({"answer": result, "tasks": task_result})
    except Exception as e:
        return jsonify({"answer": f"Error: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)



