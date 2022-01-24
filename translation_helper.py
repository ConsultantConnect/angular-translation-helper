import glob
import json
import re
from typing import Dict

import click

import settings
from json_to_po import get_and_save_po_contents
from po_to_json import update_json_translation


def _get_current_translations(language: str = "fr") -> Dict[str, str]:
    f = open(f"{settings.JSON_PATH}/{language}.json")
    data = json.load(f)
    f.close()
    return data


def _get_html_files() -> list[str]:
    directory = "src/app/"
    pathname = directory + "/**/*.html"
    files = glob.glob(pathname, recursive=True)
    return files


def _extract_translations() -> Dict[str, str]:
    TRANSLATE_TAGS_RE = r"{{\s?(\"|')(.*?)(\"|') ?\| ?translate"
    TERNARY_TRANSLATE_TAGS_RE = (
        r"(\"|')([A-Za-z ]+)(\"|') : (\"|')([A-Za-z ]+)(\"|') ?\| ?translate(\"|')"
    )
    REGEXs = [TRANSLATE_TAGS_RE, TERNARY_TRANSLATE_TAGS_RE]

    master_dict = {}

    html_files = _get_html_files()

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


def _merge_translations(language: str = "fr") -> Dict[str, str]:
    current_translations = _get_current_translations(language)
    extracted_translations = _extract_translations()
    for key, _ in extracted_translations.items():
        if key in current_translations:
            extracted_translations[key] = current_translations[key]
    return extracted_translations


@click.group()
def update_json():
    pass


@update_json.command()
@click.option("--language", default="fr", help="Target language")
def parse_to_json(language: str) -> None:
    if len(language) > 2:
        raise Exception("Language code must be 2 characters long")
    new_file_contents = _merge_translations(language)
    with open(f"{settings.JSON_PATH}/{language}.json", "w", encoding="utf-8") as f:
        json.dump(new_file_contents, f, indent=4, sort_keys=True)
        f.write("\n")


@click.group()
def json_to_po():
    pass


@json_to_po.command()
@click.option("--language", default="fr", help="Target language")
def generate_pofile(language: str) -> None:
    get_and_save_po_contents(language)


@click.group()
def po_to_json():
    pass


@po_to_json.command()
@click.option("--language", default="fr", help="Target language")
def pofile_to_json(language: str) -> None:
    update_json_translation(language)


cli = click.CommandCollection(sources=[update_json, json_to_po, po_to_json])

if __name__ == "__main__":
    cli()
