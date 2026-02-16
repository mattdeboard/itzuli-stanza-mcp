from flask import Flask, request, jsonify

from itzuli_stanza_mcp.nlp import create_pipeline, rows_to_dicts, process_input

app = Flask(__name__)
pipeline = create_pipeline()


@app.post("/stanza")
def stanza_endpoint():
    data = request.get_json()
    text = data["text"]
    rows = process_input(pipeline, text)
    return jsonify(rows_to_dicts(rows))


if __name__ == "__main__":
    app.run(port=5001)
