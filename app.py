from flask import Flask, render_template, request, jsonify, send_from_directory
from markdown2 import markdown
from pathlib import Path
import yaml
import logging
import simulation

app = Flask(__name__)

POSTS_DIRECTORY = "posts"


def load_posts():
    posts = []
    for md_file in Path(POSTS_DIRECTORY).glob("*.md"):
        with open(md_file, "r", encoding="utf-8") as file:
            content = file.read()
            if content.startswith("---"):
                _, front_matter, md_content = content.split("---", 2)
                metadata = yaml.safe_load(front_matter)
                metadata["content"] = md_content.strip()
            else:
                metadata = {
                    "title": "Untitled",
                    "description": "",
                    "image": "",
                    "content": content,
                }
            metadata["filename"] = md_file.stem
            posts.append(metadata)
    return posts


@app.route("/")
def index():
    posts = load_posts()
    return render_template("index.html", posts=posts)


@app.route("/post/<filename>")
def post(filename):
    filepath = Path(POSTS_DIRECTORY) / f"{filename}.md"
    if not filepath.exists():
        return "Post not found", 404

    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        if content.startswith("---"):
            _, front_matter, md_content = content.split("---", 2)
            metadata = yaml.safe_load(front_matter)
            content = md_content.strip()
        else:
            metadata = {"title": "Untitled"}
        html_content = markdown(content, extras=["fenced-code-blocks", "tables"])

    return render_template(
        "post.html", content=html_content, title=metadata.get("title", "Untitled")
    )


@app.route("/static/images/<path:filename>")
def images(filename):
    return send_from_directory("static/images", filename)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/run_simulation", methods=["POST"])
def run_simulation_route():
    sim_speed = float(request.form.get("sim_speed", 1.0))
    sim_duration = float(request.form.get("sim_duration", 0.1))
    simulation_data = simulation.run_simulation(sim_speed, sim_duration)
    return jsonify(simulation_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
