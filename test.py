import xml.etree.ElementTree as ET

# Pfad zur XML-Datei
file_path = "test.xml"

# XML-Datei laden
tree = ET.parse(file_path)
root = tree.getroot()

# Gewünschtes <extension>-Tag finden und bearbeiten
for extension in root.findall("extension"):
    if extension.attrib.get("point") == "xbmc.service" and extension.attrib.get("library") == "kodiinfocenter.py":
        extension.set("point", "xbmc.python.script")
        print("Das <extension>-Tag wurde geändert.")
    else:
        print("Keine Änderung")

# Änderungen speichern
tree.write(file_path, encoding="utf-8", xml_declaration=True)
