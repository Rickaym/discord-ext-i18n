import requests

src_url = "https://raw.githubusercontent.com/highlightjs/highlight.js/main/SUPPORTED_LANGUAGES.md"
res = requests.get(src_url)

records = res.text.split("<!-- LANGLIST -->")[-1].split("<!-- LANGLIST_END -->")[0].split("\n")

shortcodes = set()
for rec in records:
    if rec.strip():
        for code in rec.split("|")[2].split(","):
            shortcodes.add(code.strip().lower())
shortcodes.remove(":---------------------")
shortcodes.remove("aliases")
print(shortcodes)
