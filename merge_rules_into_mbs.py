#!/usr/bin/env python3
"""
Merge a generated Rules XML into an existing MBS_XML file by appending a <Rules> node.

Usage:
  python merge_rules_into_mbs.py /path/to/MBS-XML.xml /path/to/Rules_extracted.xml /path/to/output.xml
"""
import sys, xml.etree.ElementTree as ET

def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level + 1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    mbs_path, rules_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    mbs_tree = ET.parse(mbs_path)
    mbs_root = mbs_tree.getroot()
    rules_tree = ET.parse(rules_path)
    rules_root = rules_tree.getroot()

    # Remove existing <Rules> if present
    for existing in list(mbs_root.findall("Rules")):
        mbs_root.remove(existing)

    # Append a copy of <Rules> children under a new <Rules> node
    rules_container = ET.Element("Rules")
    for child in list(rules_root):
        rules_container.append(child)

    mbs_root.append(rules_container)
    indent(mbs_root)
    mbs_tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"Merged rules into {out_path}")

if __name__ == "__main__":
    main()
