import pydom

# Load HTML
with open("index.html", "r", encoding="utf-8") as f:
    raw = f.read()

document = pydom.Document(raw)

# Select the nav element
nav = document.getElementById("nav")

# Modify its innerHTML
nav.innerHTML = "<h1>heavens above</h1>"

document.write("may the lord have mercy upon us all")

# Save modified HTML
with open("index.html", "w", encoding="utf-8") as f:
    f.write(str(document.soup))

