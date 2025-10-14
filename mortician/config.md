## mortician - config

*Anki needs to be restarted after changing the config.*

* `again_threshold` - How many **times** a card should be
answered again within the given *timeframe* for it to be buried.
* `timeframe` - How many **hours** back answers should be counted.
* `count_from_daystart` - Ignore the *timeframe* parameter
and always count agains from the start of the
anki day (usually 4AM in the morning, configured in Anki Preferences).
* `again_notify` - Show a tooltip every time the user presses
`again` on a card showing the card's statistics.
* `tag` - This option lets you specify a tag that gets added to difficult cards.
This is useful if you want to find the cards later.
Empty string `""` disables tagging.
* `flag` - Like `tag`, but adds a [flag](https://docs.ankiweb.net/#/studying?id=editing-and-more) to the cards.
Possible values: `Red`, `Orange`, `Green`, `Blue`.
Empty string = no flag.
* `disable_tooltips` - Never show tooltips.
* `no_bury` - Never bury cards.
Though this option disables the main feature of the add-on,
you can still use it if you want to tag or flag difficult cards, but keep them in the learning queue.
* `ignore_new_cards` - Don't do anything to cards in the learning queue.

****

If you enjoy this add-on, please consider supporting my work by
**[pledging your support on Patreon](https://www.patreon.com/tatsumoto_ren)**.
Thank you so much!
