## mortician - config

*Anki needs to be restarted after changing the config.*

* `again_threshold` - How many **times** a card should be
answered again within the given *timeframe* for it to be buried.
* `timeframe` - How many **hours** back should answers be counted.
* `count_from_daystart` - Ignore the *timeframe* parameter
and always count agains from the start of the
anki day (usually 4AM in the morning, configured in Anki Preferences).
* `again_notify` - Show a tooltip every time the user presses
`again` on a card showing the card's statistics.
* `tag_on_bury` - This option lets you specify a tag
that is added to cards if they get buried by the add-on.
This is useful if you want to take action to remember them better in the future.
Empty string `""` disables tagging.
* `flag_on_bury` - Like `tag_on_bury`, but adds a flag to the card.
Possible values: `Red`, `Orange`, `Green`, `Blue`.
Empty string = no flag.
* `disable_tooltips` - Never show tooltips.

****

If you enjoy this add-on, please consider supporting my work by
**[pledging your support on Patreon](https://www.patreon.com/tatsumoto_ren)**.
Thank you so much!
