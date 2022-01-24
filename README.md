# angular-translation-helper

Workflow:

0. Create config.ini in project root based on config-example.ini
1. Run parse-to-json to collate all translations into a {language}.json file
2. Run json-to-po to convert the {language}.json file to a {language}.po file for easy editing inside Poedit
3. Run po-to-json to convert the edited pofile back to JSON for use by Angular
