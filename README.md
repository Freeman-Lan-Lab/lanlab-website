# Lan Lab website — GitHub Pages copy

Standalone copy of the eight public pages at https://www.lanlab.ca, captured September 11, 2026. The publishable website is in `dist/`. It needs no Wix account, server, database, or build service to run.

## Preview

Open `dist/index.html` in a browser, or serve the `dist` folder with a local static web server. All internal navigation uses relative paths, so the site supports either a GitHub project address or a custom domain.

## Publish on GitHub Pages

1. Create a GitHub repository, for example `lanlab-website`. A public repository supports GitHub Pages on GitHub Free.
2. Add this project's files using GitHub Desktop or Git, including the `dist` and `.github` folders. Commit and push to the `main` branch. Do not upload only the contents of `dist` when using the included workflow.
3. In the repository, open **Settings → Pages** and choose **GitHub Actions** as the source.
4. Open **Actions → Publish lab website → Run workflow**, or push another change to `main`.
5. After deployment succeeds, the Pages settings and workflow show the public website address. Review all pages there before changing the domain.

The workflow deploys only `dist`. Original capture files and local conversion dependencies are excluded by `.gitignore`.

Official instructions: [GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Move www.lanlab.ca when ready

Keep Wix serving the domain until you have reviewed the new site. Verify domain ownership in GitHub, then add `www.lanlab.ca` in the repository's Pages custom-domain settings. Only then change the `www` DNS record to the GitHub Pages hostname for your account. Configure the apex `lanlab.ca` as described in GitHub's guide and enable HTTPS when available. Preserve email-related DNS records.

No domain settings have been changed by this migration. Domain registration is separate from Wix website hosting: keep the domain registration active even if you later end the Wix website plan.

Use [GitHub's custom-domain guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) for current DNS values and instructions. This project uses Actions, so no CNAME file is required.

## What was copied and repaired

- All eight public pages retain their substantive text and linked publications.
- Original navy header, lab logo, Research dropdown and keyboard skip link are provided.
- Five Home hero slides are restored in source order, including the intentional repeated group image, with previous/next and pause/play controls.
- Recruitment and Team galleries use full-frame cropped photos with overlaid previous/next controls and enlargement. Contact shows a horizontal multi-photo strip with six unique images and scrolling controls, matching the original presentation.
- Events begins with nine images and adds six per Show More click, with gray centered captions and image enlargement. The page grows naturally without nested scrolling.
- Contact includes a Google Maps embed and direct map link for 170 College Street, Toronto. The map needs an internet connection; site text, photos, fonts, video and recruitment PDF are hosted locally.
- Mobile content fits narrow screens and uses the same substantive text. Its layout is adapted rather than a pixel-identical recreation of Wix.
- The original PI portrait crop is preserved.
- A small local `site.js` supplies interactions; Wix scripts and analytics are removed.

Browser checks covered all eight routes at 390 px and 800 px, desktop gallery controls, Events expansion and enlargement, Contact map, and the PI portrait. Custom gallery controls are functionally equivalent rather than identical to Wix's animation/UI. The domain has not been changed and GitHub deployment has not been run.

## Updating content

Edit the corresponding `dist/<page>/index.html` (`dist/index.html` for Home). Text is present in both the original desktop content and the mobile reading content; update both. Shared navigation is present in each page. `dist/migration.css` controls the standalone navigation, galleries, and mobile layout. Push changes to `main` to republish.

The HTML retains Wix's generated layout and is relatively verbose. A future rebuild using reusable templates would make ongoing content editing easier.

## Conversion and checks

`migrate.py` and `site_components.py` recreate the static HTML from the archived public captures, downloads media, and records the source-to-local asset mapping in `migration-report.json`. It requires Python with Beautiful Soup and optionally Pillow. Running it overwrites the generated HTML, so preserve manual changes first. Existing captures are reused; it is not an automatic live-site synchronization tool.

`validate.py` checks every local page link and asset reference, CSS URL, unexpected runtime dependency, and file-size limit. It does not test remote publication links or visual layout. Run it after edits. The GitHub deployment itself has not been run yet.
