#!/usr/bin/env python3
"""
CHAIN NETWORK - automated release bot.

Runs on a GitHub Actions schedule. When the next queued subject's four videos
are public on YouTube, it rebuilds the site, pushes the deploy, verifies the
live site, then announces on the five Telegram channels.

Secrets (GitHub Actions repository secrets, set by Mike only):
  RELEASE_QUEUE        JSON: queued subjects with video IDs and approved posts
  TELEGRAM_BOT_TOKEN   the @TheChainNetworkBot token
  BLOTATO_API          Blotato API key, used to post to X @TheChainNetwork
                       (account 21431). Optional: if absent, X is skipped.

The trigger and the approval are the same act: Mike flipping all four videos
of a subject to Public. Post copy is pre-approved by Mike in the queue.
No secret is ever written to the repo, to logs or to any file.
"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "catalog_data.json")
RELEASES = os.path.join(HERE, "RELEASES.json")
LANGS = ["en", "es", "pt", "hi"]
CHATS = {
    "main": "@TheChainNetwork",
    "en": "@TheChainNetworkEN1",
    "es": "@TheChainNetworkES",
    "pt": "@TheChainNetworkBR",
    "hi": "@TheChainNetworkIN",
}


def http_json(url, data=None):
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def is_public(video_id):
    """True when the watch-URL oEmbed responds. House rule: never youtu.be,
    YouTube serves stale empty results on short-link keys for videos that
    were once private (learnt the hard way with subject 11)."""
    watch = urllib.parse.quote(f"https://www.youtube.com/watch?v={video_id}", safe="")
    try:
        return bool(http_json(f"https://www.youtube.com/oembed?format=json&url={watch}").get("title"))
    except Exception:
        return False


def run(*cmd):
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=HERE)


def git_push(message):
    run("git", "add", "-A")
    staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=HERE)
    if staged.returncode != 0:
        run("git", "commit", "-m", message)
        run("git", "push")


def send(token, chat, text):
    data = urllib.parse.urlencode({"chat_id": chat, "text": text}).encode()
    resp = http_json(f"https://api.telegram.org/bot{token}/sendMessage", data)
    if not resp.get("ok"):
        raise RuntimeError(f"sendMessage failed for {chat}: {resp}")
    print("SENT", chat)


def post_to_x(api_key, text):
    """Publish the release post to X @TheChainNetwork (Blotato account 21431).
    Never posts to the Better Connected account, which is handled in-house."""
    body = json.dumps({"post": {
        "accountId": "21431",
        "target": {"targetType": "twitter"},
        "content": {"text": text, "platform": "twitter", "mediaUrls": []},
    }}).encode()
    req = urllib.request.Request("https://backend.blotato.com/v2/posts", data=body,
                                 headers={"blotato-api-key": api_key,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("SENT X @TheChainNetwork", r.status)


def main():
    queue = json.loads(os.environ["RELEASE_QUEUE"])["subjects"]
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    releases = json.load(open(RELEASES)) if os.path.exists(RELEASES) else {}
    queue.sort(key=lambda s: s["n"])
    subj = next((s for s in queue if releases.get(s["n"]) != "announced"), None)
    if subj is None:
        print("Queue empty, nothing to do.")
        return
    n = subj["n"]

    if releases.get(n) != "built":
        public = {l: is_public(subj["videos"][l]) for l in LANGS}
        if not all(public.values()):
            print(f"Subject {n} not fully public yet: {public}")
            return
        print(f"Subject {n} public in all four languages, building site.")
        cat = json.load(open(CATALOG, encoding="utf-8"))
        if n not in {s["n"] for s in cat["subjects"]}:
            cat["subjects"].append({"n": n, "level": subj["level"], "tag": subj["tag"], "title": subj["titles"]})
            cat["subjects"].sort(key=lambda s: s["n"])
        cat["levels"].setdefault(subj["level"], subj["level_label"])
        with open(CATALOG, "w", encoding="utf-8") as f:
            json.dump(cat, f, ensure_ascii=False, indent=2)

        # Recreate the links file where build_site.py expects it, from the
        # current public catalogue plus this subject's four links.
        build_dir = os.path.join(os.path.dirname(HERE), "02_Build - The Chain Network")
        os.makedirs(build_dir, exist_ok=True)
        vids = json.load(open(os.path.join(HERE, "videos.json"), encoding="utf-8"))["videos"]
        lines = {f"{v['language'].upper()} {v['subject_n']} = https://youtu.be/{v['video_id']}" for v in vids}
        lines |= {f"{l.upper()} {n} = https://youtu.be/{subj['videos'][l]}" for l in LANGS}
        with open(os.path.join(build_dir, "TCN VIDEO LINKS - paste here.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(lines)) + "\n")

        run(sys.executable, "build_site.py")
        releases[n] = "built"
        with open(RELEASES, "w") as f:
            json.dump(releases, f, indent=1)
        git_push(f"Release bot: subject {n} live on YouTube, site rebuilt")

    # Verify the live site is serving the new build before announcing.
    want = len(json.load(open(os.path.join(HERE, "videos.json"), encoding="utf-8"))["videos"])
    for _ in range(16):
        try:
            live = http_json(f"https://thechainnetwork.com/videos.json?rb={int(time.time())}")
            if live.get("count") == want:
                print("Live site verified at", want, "records.")
                break
        except Exception:
            pass
        time.sleep(30)
    else:
        print("WARNING: live count not confirmed within 8 minutes, announcing anyway.")

    for key in ["main"] + LANGS:
        send(token, CHATS[key], subj["posts"][key])
        time.sleep(1)
    blotato = os.environ.get("BLOTATO_API")
    if blotato and subj["posts"].get("x"):
        try:
            post_to_x(blotato, subj["posts"]["x"])
        except Exception as e:
            print("WARNING: X post failed, Telegram and site are done:", e)
    releases[n] = "announced"
    with open(RELEASES, "w") as f:
        json.dump(releases, f, indent=1)
    git_push(f"Release bot: subject {n} announced on Telegram")
    print(f"Subject {n} released and announced.")


if __name__ == "__main__":
    main()
