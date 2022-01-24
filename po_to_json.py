import json
from typing import Dict
import polib


def po_to_dict(language: str = "fr") -> Dict[str, str]:
    po_dict = {}
    pofile = polib.pofile(f"../src/assets/i18n/{language}.po")
    for entry in pofile:
        po_dict[entry.msgid] = entry.msgstr
    return po_dict


def update_json_translation(language: str = "fr") -> None:
    if len(language) > 2:
        raise Exception("Language code must be 2 characters long")
    new_file_contents = po_to_dict(language)
    json_formatted_str = json.dumps(new_file_contents, indent=4, sort_keys=True)
    f = open(f"../src/assets/i18n/{language}.json", "w")
    f.write(json_formatted_str)
    f.close()

update_json_translation()
