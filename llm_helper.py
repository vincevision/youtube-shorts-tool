import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in .env")

client = Groq(api_key=GROQ_API_KEY)


def generate_trending_people(niche, region):
    """
    Suggest currently relevant public figures / celebrities for a niche/region.
    """
    prompt = f"""
You are a trends analyst for YouTube Shorts.

Niche: {niche or "general entertainment"}
Region: {region or "global"}

Task:
1. List 5 public figures / celebrities / influencers who are currently relevant,
   talked about, or frequently searched within this niche and region.
2. Focus on names where ongoing or repeat content about them performs well
   (e.g. star athletes, top musicians, politicians, creators, etc.).
3. Avoid made-up people.

Format EXACTLY as:

1) <person name>
2) <person name>
3) <person name>
4) <person name>
5) <person name>
"""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful trends analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )

    text = resp.choices[0].message.content
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    people = []
    for line in lines:
        if ")" in line:
            parts = line.split(")", 1)
            name = parts[1].strip(" -–:")
            if name:
                people.append(name)

    return people[:5]


def generate_trending_topics(celebrity, niche, style, region):
    """
    Ask the model to propose a few 'currently plausible' viral topics.
    """
    prompt = f"""
You are a viral content strategist for YouTube Shorts.

Celebrity / Public Figure: {celebrity}
Niche / Angle: {niche}
Video Style: {style}
Target Region: {region or "global"}

Task:
1. Propose 5 highly clickable, *plausible* trending video topic ideas
   that someone could make *today* about this person, in this niche.
2. They should feel current and viral (controversies, big wins, big losses,
   recent moves, comparisons, Top 5 lists, before/after, "what nobody tells you", etc.).
3. Do NOT invent specific fake news. Keep it general or based on well-known patterns.

Format your response as:

1) <short topic phrase, max 80 characters>
2) <...>
3) <...>
4) <...>
5) <...>
"""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful viral content strategist."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )

    text = resp.choices[0].message.content
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    topics = []
    for line in lines:
        if ")" in line:
            parts = line.split(")", 1)
            topic = parts[1].strip(" -–:")
            if topic:
                topics.append(topic)

    topics = topics[:5]
    if not topics:
        # Fallback if parsing fails
        topics = [
            f"Inside the rise of {celebrity}",
            f"Why {celebrity} is dominating {niche or 'their niche'}",
            f"The truth about {celebrity} nobody talks about",
            f"Top 5 facts about {celebrity}",
            f"How {celebrity} changed the game in {niche or 'their field'}",
        ]

    return topics


def generate_youtube_assets(celebrity, niche, style, region, chosen_topic):
    """
    Generate titles, description, tags for the chosen topic.
    """
    prompt = f"""
You are an expert YouTube Shorts strategist.

Celebrity / Public Figure: {celebrity}
Niche / Angle: {niche}
Video Style: {style}
Target Region: {region or "global"}
Chosen topic: {chosen_topic}

Task:
1. Generate 10 viral YouTube Shorts titles (max 70 characters each),
   optimized for high CTR but NOT misleading or defamatory.
2. Generate 1 strong YouTube Shorts description (~2–3 sentences) with:
   - a hook in the first line
   - 5–10 relevant hashtags at the end
3. Generate 20 SEO-friendly tags (single words or short phrases)
   that match the topic & niche.

Format EXACTLY as:

TITLES:
1. ...
2. ...
3. ...
4. ...
5. ...
6. ...
7. ...
8. ...
9. ...
10. ...

DESCRIPTION:
<one multi-line description here>

TAGS:
tag1, tag2, tag3, ...
"""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert YouTube Shorts strategist."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )

    text = resp.choices[0].message.content

    titles = []
    description_lines = []
    tags = []

    section = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("TITLES"):
            section = "titles"
            continue
        if upper.startswith("DESCRIPTION"):
            section = "description"
            continue
        if upper.startswith("TAGS"):
            section = "tags"
            continue

        if section == "titles":
            if line[0].isdigit() and "." in line:
                parts = line.split(".", 1)
                title = parts[1].strip()
                if title:
                    titles.append(title)
        elif section == "description":
            description_lines.append(line)
        elif section == "tags":
            tags = [t.strip() for t in line.split(",") if t.strip()]

    description = "\n".join(description_lines).strip()

    # Fallbacks
    if not titles:
        titles = [
            chosen_topic,
            f"{celebrity}: what nobody is telling you",
            f"Top 5 {niche or 'facts'} about {celebrity}",
        ]

    if not description:
        description = (
            f"{celebrity} is making waves again – here's what you need to know about '{chosen_topic}'.\n\n"
            "#shorts #viral #trending"
        )

    if not tags:
        tags = [
            celebrity,
            f"{celebrity} shorts",
            "viral shorts",
            "trending",
            "news",
            niche or "celebrity",
            "shorts",
        ]

    return {
        "titles": titles,
        "description": description,
        "tags": tags,
    }