import glob
import json
import re
from typing import Dict, List

import click

import settings
from json_to_po import get_and_save_po_contents
from po_to_json import update_json_translation


def _get_current_translations(language: str = "cy") -> Dict[str, str]:
    try:
        f = open(f"{settings.JSON_PATH}/{language}.json")
    except FileNotFoundError:
        return {}
    data = json.load(f)
    f.close()
    return data


def _get_html_files() -> List[str]:
    directory = settings.HTML_FILES_PATH
    pathname = directory + "/**/*.html"
    files = glob.glob(pathname, recursive=True)
    return files


def _get_ts_files() -> List[str]:
    directory = settings.HTML_FILES_PATH
    pathname = directory + "/**/*.ts"
    files = glob.glob(pathname, recursive=True)
    return files


def _extract_translations() -> Dict[str, str]:
    TRANSLATE_TAGS_RE = r"{{\s?(\"|')((.|\n)*?)(\"|') ?\|(.|\n)*?"
    TERNARY_TRANSLATE_TAGS_RE = (
        r"(\"|')([A-Za-z ]+)(\"|') : (\"|')([A-Za-z ]+)(\"|') ?\| ?translate(\"|')"
    )
    OR_TRANSLATE_TAGS_RE = r"\|\| ?'(.*?)' ?\| ?translate ?}}"
    INNER_HTML_RE = r"\[innerHTML\]=(\"|\')(\"|\')(.*?)(\"|\') ?| ?translate"
    APPTOOLTIP_RE = r"\[appTooltip\]=(\"|\')(\"|\')(.*?)(\"|\') ?| ?translate"
    HEADER_RE = r"header=(\"|\'){{(\"|\')(.*?)(\"|\') ?| ?translate"
    MSG_RE = r"msg=(\"|\'){{(\"|\')(.*?)(\"|\') ?| ?translate"
    TEXT_RE = r"\[text\]=(\"|\')(\"|\')(.*?)(\"|\') ?| ?translate"
    TRANSLATE_COMMENT_RE = r"<!-- translate: \"(.*)\" -->"
    ARIA_LABEL_RE = r"aria-label=\"\'(.+)\'\s?\|\s?translate\""
    HTML_REGEXs = [
        TRANSLATE_TAGS_RE,
        TERNARY_TRANSLATE_TAGS_RE,
        OR_TRANSLATE_TAGS_RE,
        INNER_HTML_RE,
        APPTOOLTIP_RE,
        HEADER_RE,
        MSG_RE,
        TEXT_RE,
        TRANSLATE_COMMENT_RE,
        ARIA_LABEL_RE,
    ]

    TRANSLATE_SERVICE_RE = r"this\.translate\.get\(\n +\'(.*)\',|translate\.get\(\B'((.|\n)*?)'\B(, {.*})?\)(\.subscribe|\.toPromise)|translate\.get\((`|\")((.|\n)*?)(`|\")|this\.translate\n\s+\.get\(('|\")(.*)('|\")|this\.translate\n\s+\.get\(\n\s+('|\")(.*)('|\")|translate\n\s+\.get\(('|\")(.*)('|\")|translate\n\s+\.get\(('|\"|`)(.*)('|\"|`)"  # noqa
    TAB_LABEL_RE = r"Tab\((\"|\').*?(\"|\'), ?(\"|\')(.*?)(\"|\'), (\"|\').*(\"|\')"
    TRANSPROP_RE = r"\'(.*)\'(;|,)? \/\/ transProp"
    TS_REGEXs = [TRANSLATE_SERVICE_RE, TAB_LABEL_RE, TRANSPROP_RE]

    master_dict = {}

    html_files = _get_html_files()
    ts_files = _get_ts_files()

    html_matches = _get_regex_matches(HTML_REGEXs, html_files)
    ts_matches = _get_regex_matches(TS_REGEXs, ts_files)

    master_dict.update(html_matches)
    master_dict.update(ts_matches)

    return master_dict


def _get_regex_matches(regexes: List[str], files: List[str]):
    out = {}
    for file in files:
        file_handler = open(
            file,
            "r",
        )
        file_text = file_handler.read()
        file_handler.close()

        for regex in regexes:
            matches = re.findall(regex, file_text)
            # flatten list, if required
            if any(isinstance(el, (list, tuple)) for el in matches):
                matches = [item for sublist in matches for item in sublist]
            # remove dupes, ignore quotes
            matches = [
                match.replace("&amp;", "&")
                for match in set(matches)
                if (
                    match != '"'
                    and match != "'"
                    and len(match) > 1
                    and match[0] != ","
                    and match not in (".subscribe", ".toPromise")
                )
            ]
            match_dict = {}
            for match in matches:
                match = match.replace("\n", "").replace("\r", "").replace("\\", "")
                if match[-1] == " ":
                    match = " ".join(match.split()) + " "
                else:
                    match = " ".join(match.split())
                match_dict[match] = ""
            out.update(match_dict)
    return out


def _merge_translations(language: str = "cy") -> Dict[str, str]:
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
@click.option("--language", default="cy", help="Target language")
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
@click.option("--language", default="cy", help="Target language")
def generate_pofile(language: str) -> None:
    get_and_save_po_contents(language)


@click.group()
def po_to_json():
    pass


@po_to_json.command()
@click.option("--language", default="cy", help="Target language")
def pofile_to_json(language: str) -> None:
    update_json_translation(language)


@click.group()
def update_en():
    pass


@update_en.command()
@click.option("--srclang", default="cy", help="Source language")
def update_en_vars(srclang: str) -> None:
    if len(srclang) > 2:
        raise Exception("Language code must be 2 characters long")
    elif srclang == "en":
        raise Exception("Cannot update English translations")

    srclang_translations = _get_current_translations(srclang)
    en_translations = _get_current_translations("en")

    srclang_translations = {
        key: value for key, value in srclang_translations.items() if "{{" in key
    }

    fr_var_keys = list(srclang_translations.keys())
    en_keys = list(en_translations.keys())

    new_keys = [key for key in fr_var_keys if key not in en_keys]

    for key in new_keys:
        en_translations[key] = key

    with open(f"{settings.JSON_PATH}/en.json", "w", encoding="utf-8") as f:
        json.dump(en_translations, f, indent=4, sort_keys=True)
        f.write("\n")


cli = click.CommandCollection(sources=[update_json, json_to_po, po_to_json, update_en])

if __name__ == "__main__":
    cli()
