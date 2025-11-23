import os
import random

from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

from llm_helper import (
    generate_trending_people,
    generate_trending_topics,
    generate_youtube_assets,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1 GB


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        celeb = (request.form.get("celebrity") or "").strip()
        niche = (request.form.get("niche") or "").strip()
        style = request.form.get("style") or "Commentary"
        region = (request.form.get("region") or "").strip()
        auto_mode = request.form.get("auto_mode") == "on"

        session["niche"] = niche
        session["style"] = style
        session["region"] = region

        if auto_mode:
            # 1) Auto-pick person
            try:
                people = generate_trending_people(niche, region)
            except Exception as e:
                return render_template("index.html", error=f"Error from AI (people): {e}")

            if not people:
                auto_celeb = "a trending public figure"
            else:
                auto_celeb = random.choice(people)

            session["celeb"] = auto_celeb

            # 2) Generate topics
            try:
                topics = generate_trending_topics(auto_celeb, niche, style, region)
            except Exception as e:
                return render_template("index.html", error=f"Error from AI (topics): {e}")

            session["topics"] = topics

            # 3) Auto-pick topic
            if topics:
                chosen_topic = random.choice(topics)
            else:
                chosen_topic = f"Hot topic about {auto_celeb} in {niche or 'their niche'}"

            session["chosen_topic"] = chosen_topic

            # 4) Go straight to result
            return redirect(url_for("result"))

        else:
            if not celeb:
                return render_template("index.html", error="Please enter a celebrity/public figure (or enable auto mode).")

            session["celeb"] = celeb

            try:
                topics = generate_trending_topics(celeb, niche, style, region)
            except Exception as e:
                return render_template("index.html", error=f"Error from AI: {e}")

            session["topics"] = topics
            return redirect(url_for("topics"))

    return render_template("index.html")


@app.route("/topics", methods=["GET", "POST"])
def topics():
    topics = session.get("topics") or []
    celeb = session.get("celeb", "")

    if not topics:
        return redirect(url_for("index"))

    if request.method == "POST":
        chosen_index = request.form.get("chosen_topic")
        if chosen_index is None:
            return render_template("topics.html", topics=topics, celeb=celeb, error="Please select a topic.")
        try:
            chosen_index = int(chosen_index)
        except ValueError:
            chosen_index = 0

        if chosen_index < 0 or chosen_index >= len(topics):
            chosen_index = 0

        session["chosen_topic"] = topics[chosen_index]
        return redirect(url_for("result"))

    return render_template("topics.html", topics=topics, celeb=celeb)


@app.route("/result")
def result():
    celeb = session.get("celeb", "")
    niche = session.get("niche", "")
    style = session.get("style", "")
    region = session.get("region", "")
    chosen_topic = session.get("chosen_topic", "")

    if not chosen_topic:
        return redirect(url_for("index"))

    try:
        assets = generate_youtube_assets(celeb, niche, style, region, chosen_topic)
    except Exception as e:
        return render_template(
            "result.html",
            celeb=celeb,
            niche=niche,
            style=style,
            region=region,
            topic=chosen_topic,
            titles=[],
            description=f"Error generating assets: {e}",
            tags=[],
        )

    return render_template(
        "result.html",
        celeb=celeb,
        niche=niche,
        style=style,
        region=region,
        topic=chosen_topic,
        titles=assets["titles"],
        description=assets["description"],
        tags=assets["tags"],
    )


@app.route("/upload", methods=["POST", "GET"])
def upload_page():
    from werkzeug.utils import secure_filename
    from youtube_uploader import upload_video

    if request.method == "POST" and "selected_title" in request.form:
        # Step 1: from result page with metadata
        selected_title = (request.form.get("selected_title") or "").strip()
        description = request.form.get("description") or ""
        tags_str = request.form.get("tags") or ""
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        session["selected_title"] = selected_title
        session["selected_description"] = description
        session["selected_tags"] = tags

        return render_template(
            "upload.html",
            title=selected_title,
            description=description,
            tags=tags,
            youtube_url=None,
            error=None,
        )

    elif request.method == "POST" and "video_file" in request.files:
        file = request.files["video_file"]
        title = session.get("selected_title", "Untitled Short")
        description = session.get("selected_description", "")
        tags = session.get("selected_tags", [])

        if file.filename == "":
            return render_template(
                "upload.html",
                title=title,
                description=description,
                tags=tags,
                youtube_url=None,
                error="Please select a video file.",
            )

        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(video_path)

        try:
            youtube_url = upload_video(
                video_file=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status="unlisted",
            )
        except Exception as e:
            return render_template(
                "upload.html",
                title=title,
                description=description,
                tags=tags,
                youtube_url=None,
                error=f"Error uploading to YouTube: {e}",
            )

        return render_template(
            "upload.html",
            title=title,
            description=description,
            tags=tags,
            youtube_url=youtube_url,
            error=None,
        )

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)