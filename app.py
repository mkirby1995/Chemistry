from flask import Flask, render_template, send_from_directory
from markdown2 import markdown
from pathlib import Path
import os

app = Flask(__name__)

# Define the posts directory
POSTS_DIRECTORY = "posts"

# Load the posts metadata for thumbnails
def load_posts():
    posts = []
    for md_file in Path(POSTS_DIRECTORY).glob("*.md"):
        with open(md_file, "r") as file:
            lines = file.readlines()
            title = lines[0].replace("#", "").strip()
            description = lines[1].strip() if len(lines) > 1 else ""
            posts.append({
                "title": title,
                "description": description,
                "filename": md_file.stem
            })
    return posts

@app.route('/')
def index():
    posts = load_posts()
    return render_template("index.html", posts=posts)

@app.route('/post/<filename>')
def post(filename):
    filepath = Path(POSTS_DIRECTORY) / f"{filename}.md"
    if not filepath.exists():
        return "Post not found", 404

    with open(filepath, "r") as file:
        content = markdown(file.read(), extras=["fenced-code-blocks", "tables"])
    
    return render_template("post.html", content=content)

@app.route('/static/images/<filename>')
def images(filename):
    return send_from_directory("static/images", filename)

if __name__ == "__main__":
    app.run(debug=True)
