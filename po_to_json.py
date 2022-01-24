import json
from typing import Dict

import polib

import settings


def po_to_dict(language: str = "fr") -> Dict[str, str]:
    po_dict = {}
    pofile = polib.pofile(f"{settings.JSON_PATH}/{language}.po")
    for entry in pofile:
        po_dict[entry.msgid] = entry.msgstr
    return po_dict


def update_json_translation(language: str = "fr") -> None:
    if len(language) > 2:
        raise Exception("Language code must be 2 characters long")
    new_file_contents = po_to_dict(language)
    json_formatted_str = json.dumps(new_file_contents, indent=4, sort_keys=True)
    f = open(f"{settings.JSON_PATH}/{language}.json", "w")
    f.write(json_formatted_str)
    f.write("\n")
    f.close()
