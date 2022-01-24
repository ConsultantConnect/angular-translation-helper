import glob
import json
import re
from typing import Dict


def get_current_translations(language: str = "fr") -> Dict[str, str]:
    f = open(f"../src/assets/i18n/{language}.json")
    data = json.load(f)
    f.close()
    return data


def get_html_files() -> list[str]:
    directory = "../src/app/"
    pathname = directory + "/**/*.html"
    files = glob.glob(pathname, recursive=True)
    return files


def extract_translations() -> Dict[str, str]:
    TRANSLATE_TAGS_RE = r"{{\s?(\"|')(.*?)(\"|') ?\| ?translate"
    TERNARY_TRANSLATE_TAGS_RE = (
        r"(\"|')([A-Za-z ]+)(\"|') : (\"|')([A-Za-z ]+)(\"|') ?\| ?translate(\"|')"
    )
    REGEXs = [TRANSLATE_TAGS_RE, TERNARY_TRANSLATE_TAGS_RE]

    master_dict = {}

    html_files = get_html_files()

    for html_file in html_files:
        file_handler = open(
            html_file,
            "r",
        )
        file_text = file_handler.read()
        file_handler.close()

        for regex in REGEXs:
            matches = re.findall(regex, file_text)
            # flatten matches
            matches = [item for sublist in matches for item in sublist]
            # remove dupes, ignore quotes
            matches = [
                match.replace("&amp;", "&")
                for match in set(matches)
                if (match != '"' and match != "'")
            ]
            match_dict = {match: "" for match in matches}
            master_dict.update(match_dict)

    return master_dict


def merge_translations(language: str = "fr") -> Dict[str, str]:
    current_translations = get_current_translations(language)
    extracted_translations = extract_translations()
    for key, _ in extracted_translations.items():
        if key in current_translations:
            extracted_translations[key] = current_translations[key]
    return extracted_translations


def update_translation(language: str = "fr") -> None:
    if len(language) > 2:
        raise Exception("Language code must be 2 characters long")
    new_file_contents = merge_translations(language)
    json_formatted_str = json.dumps(new_file_contents, indent=4, sort_keys=True)
    print(json_formatted_str)


update_translation()
