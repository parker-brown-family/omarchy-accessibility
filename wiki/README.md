# The evidence

Every decision points to findings, every finding to sources, and every source to its own words.

- [Decisions](decisions/): what was chosen, by whom, and what would change it.
- [Findings](findings/): one claim each, with how strong it is.
- [Sources](sources/): what was read, how much of it, and its limits.

To argue with a decision, add a source and change a finding. A replaced decision is kept, marked `superseded`, and names the one that replaced it.

`python3 tools/check_wiki.py` checks every link, and checks each quotation against the copy it was taken from. Those copies belong to their authors and are not published, so a fresh clone reports the quotations as unchecked.

No blind person has reviewed any of this yet.
