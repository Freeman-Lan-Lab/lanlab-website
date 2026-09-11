# Wix versus GitHub-ready website comparison

Independent comparison agent review, September 11, 2026. Original: https://www.lanlab.ca/. Copy: http://127.0.0.1:8765/ served from `dist/`; the copy has not been published to GitHub. This is a read-only review of the site. No website files were changed.

## Prioritized handoff to the generating agent

| Priority | Route | Original versus copy | Repair task |
| --- | --- | --- | --- |
| High | All routes, mobile | At a 390 px viewport the copy's body and header remain 980 px wide. The logo is centered around x=490 and is off-screen. Navigation is clipped after the first few links, and a horizontal scrollbar is visible. All eight routes reproduce the 980 px body width. | Remove inherited fixed desktop widths from every relevant outer wrapper and header. Verify 390 px and 800 px layouts have no horizontal overflow and all navigation items are reachable. This takes priority over stylistic mobile differences. |
| High | `/join-us/` | Wix displays an interactive Google Map beside the address. The copy removes it entirely, leaving only the background photograph in that area. The address and email remain. | Restore a supported map embed, or at minimum a clearly labeled map link with an intentional layout. Preserve the location, 170 College St, Toronto. |
| High | `/join-us/` | The replacement gallery contains 30 photos: the same six-image sequence is repeated five times. Mobile shows a single gallery with all 30 images, creating a long repeated sequence. Desktop crops the next grid row at the gallery boundary. Wix uses an interactive photo strip/carousel. | Deduplicate by the original gallery item ID or normalized asset URL before constructing the gallery. Preserve six unique items in source order. Replace the fixed-height overflowing grid with a correctly sized gallery or carousel. |
| Medium | `/` | Wix's hero changes slides and has Previous/Next controls. The copy stays on the Toronto skyline image and has no controls. During comparison Wix showed University of Toronto imagery while the copy stayed on the skyline. The recruitment gallery similarly loses its slideshow controls and 1/6 indicator. | Restore all hero slides with accessible previous/next behavior and the original ordering; implement the recruitment gallery behavior. Do not interpret a changing slide as a newly changed live-site asset. |
| Medium | `/events/` | Wix shows a three-column photo gallery with gray centered caption bands, image enlargement controls and Show More. The copy uses shorter, differently cropped images, white left-aligned caption areas with dates joined by an em dash, wider gaps, and an internal scrollbar. It exposes 32 items immediately instead of the initial nine. | Match image aspect ratios/crops and caption styling; restore progressive expansion and image enlargement, or provide an equivalent accessible gallery. Avoid nested scrolling and fixed-height clipping. The additional items are captured gallery content, not invented text. |
| Medium | All routes | The navy header color is now visually consistent. Wix has Home, a Research dropdown, Publications, The PI, Team, Events, Contact. The copy expands Research into Microfluidics and Microbiome, shifts the menu left, moves lettering vertically, and adds an active-link underline. | Restore the Research grouping and match desktop alignment/spacing while retaining accessible keyboard behavior. Fix mobile sizing first. |
| Medium | `/team/` and other galleries | Wix's Team gallery exposes a Next Item control and an image popup. The copy replaces it with a grid and no corresponding interaction. Gallery replacement also changes the reading experience elsewhere. | Reuse one accessible gallery implementation and verify unique items, source order, image associations and complete visibility on both viewport sizes. |
| Low | All routes | Wix exposes a Skip to Main Content control. The copy removes it. | Add a keyboard-visible skip link targeting the actual visible main region for each viewport. |
| Low | `/the-pi/` | The same portrait is present, but the circular crop differs: Wix's visible portrait area starts around y=100; the copy starts around y=132 with the bottom roughly aligned. | Match original crop, dimensions and positioning after higher-priority items are corrected. |

## Text completeness findings

- All eight routes were opened on the live Wix site and local copy. Desktop rendered body text was compared line by line after normalizing whitespace and invisible characters.
- Home, Microfluidics, Microbiome, Publications, The PI, Team and Contact have the same substantive text. Differences are navigation/accessibility controls and gallery counters. No new live-site prose changes were identified.
- Publications is no longer empty. The current list, including the visible 2024 and 2023 entries, was visually verified against Wix.
- Team names, current-member biographies, roles, affiliations and alumni text are present. The top Team layout and Xinyao's visible text match the original apart from the header.
- The mobile copy was checked across all eight routes against the live desktop text. No substantive prose omissions were found. Repeated Team role and affiliation labels survive because the generator deduplicates rich-text blocks, not individual role lines. The suspected role-deletion bug was not reproduced.
- Team mobile image/text order was inspected: names/biographies remain associated with the corresponding portraits, and alumni portraits retain adjacent names. Some mobile sections contain multiple people, rather than a separate card for each person.
- Events combines the original title and date into one caption. For example, "Tereza's Birthday!" and "July 2026" become "Tereza's Birthday! — July 2026". The source typo/date "Send-off for Chris — April 2027" also exists on live Wix; do not silently correct it as a migration bug.

## Checked scope and limits

- Desktop viewport screenshots compared for all eight routes; detailed visual checks on Home, Team, Events, and the bottom of Contact. Publications and research-page top sections look broadly consistent after previous text/header fixes.
- Measured body widths and inspected mobile rendered text at 390 px for all routes. Mobile copy screenshot confirms clipped header/logo and horizontal overflow. The browser viewport override applied to the copy tab only, so this is not a pixel-for-pixel comparison with Wix's actual mobile rendering. The override was reset after inspection.
- Reviewed `dist/migration.css`, `migrate.py` mobile extraction structure, and captured asset metadata as supporting evidence. Live Wix remained authoritative for current text and visible interactions.
- Off-screen lazy images can initially have empty currentSrc/naturalWidth; those initial states were not classified as broken assets without scrolling verification. External article links, complete video playback, every expanded gallery item, all hover states, and actual GitHub hosting were not exhaustively tested.
- Recommended implementation order: responsive overflow; duplicate/clipped galleries and map; slideshow/gallery interactions; navigation fidelity; final desktop/mobile regression review. Regenerate through `migrate.py` so fixes survive rebuilding, then refresh the ZIP only after verification.

## Repair follow-up

The implementation now addresses the listed findings:

- All eight pages fit the tested 390 px and 800 px viewports without horizontal overflow.
- Contact map and direct location link restored; embed visually verified at 170 College Street.
- Contact gallery reduced to six unique images. Contact and Team gallery dimensions checked to prevent clipping.
- All five hero slides restored in original order, including the intentionally repeated group image, with previous/next and pause/play. Recruitment and Team carousel controls restored.
- Events uses gray centered title/date captions, starts with nine items, and expands by six; verified 9 → 15, natural page growth, and photo enlargement.
- Research dropdown, original navy styling, desktop header placement and keyboard skip link restored. Skip link focuses the visible main content.
- Original PI crop restored. Browser comparison shows the portrait at y=133, 334 × 334 pixels on both Wix and the copy; the earlier y=100 observation was not reproduced in the final live comparison.
- Local JavaScript syntax and all eight pages' local resource/link checks pass. The map is the only intentional external embedded service.

Custom gallery controls are equivalent replacements, not a pixel-identical reproduction of Wix transitions. The copy remains local and has not been deployed to GitHub. No DNS settings were changed.
