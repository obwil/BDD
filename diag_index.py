import pathlib
content = pathlib.Path("static/index.html").read_text(encoding="utf-8")
idx = content.find("toggleEdit")
print(repr(content[idx-60:idx+160]))
