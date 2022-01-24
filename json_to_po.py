import json
from typing import Dict


def get_current_translations(language: str = "fr") -> Dict[str, str]:
    f = open(f"../src/assets/i18n/{language}.json")
    data = json.load(f)
    f.close()
    return data

def translation_to_po(language: str = "fr") -> str:
    po_contents = ""
    translations = get_current_translations(language)
    for key, value in translations.items():
        po_contents += f"msgid \"{key}\"\n"
        po_contents += f"msgstr \"{value}\"\n\n"
    return po_contents

def get_and_save_po_contents(language: str = "fr") -> None:
    contents = translation_to_po(language)
    f = open(f"../src/assets/i18n/{language}.po", "w")
    f.write(contents)
    f.close()

get_and_save_po_contents()
