# Zotero relation maker

Use this script to fill the "Related" field in [Zotero](https://www.zotero.org/) with references and citations from other items present in the library.
References and citations are coming from [Semantic Scholar](https://www.semanticscholar.org/) using the DOI. As it uses the Zotero API, there is no need to have a local Zotero installed, and it can be run from anywhere.

## Usage

Launch `relation_maker.py` once to create a `secret.json` file. Fill `library_id` with your Zotero `userID` and `api_key` with a [private key with read and write access](https://www.zotero.org/settings/keys) before launching again.

Warning: [backing up your Zotero data directory](https://www.zotero.org/support/zotero_data#backing_up_your_zotero_data) first is strongly recommended.
