# Dynamic Tech Experts MVP

Modular Django corporate website with English as the default and a Persian (RTL) language switch. Products, features, specifications,
projects, customer organizations, public image library, company profile, and contact/demo inquiries.
No deployments or installation models. Documentation, support, memberships, licensing, versions,
and private downloads are deferred. The custom user model is established for future portal work.

## Run locally (CMD)

```cmd
cd /d D:\Useful_Documents\Projects\techexpert
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

If .env does not exist yet, copy .env.example to .env and set DJANGO_SECRET_KEY.
The current workspace already has .env configured.

```cmd
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and manage content at /admin/. Press Ctrl+C to stop.
SQLite is the database, stored at db.sqlite3 in the project root. No database service,
credentials, or DB_ENGINE environment variable is needed. Existing SQLite data is preserved.
Django automatically loads the project-root .env using python-dotenv. Variables explicitly
set in the shell take precedence. The .env file is excluded from version control; the
.env.example file documents the supported settings without including secrets.

## Content workflow

1. Enter CompanyProfile information (one company record).
2. Upload public raster images in Media assets, with descriptive alt text.
3. Create categories and products. Add features, specifications and ordered screenshots
   directly on the product editing page. Publish and feature selected products.
4. Create customer organizations and industries, then projects. Use the separate
   public_customer_name field only for approved customer attribution. Check
   publication_authorized before publishing. Link products and ordered images inline.
5. Contact and demo submissions appear under Inquiries; mark them handled after follow-up.
   The MVP stores inquiries in Admin; it does not send email or notifications.

Product and project detail pages are generated automatically from database records.
Draft records are inaccessible on the public site, including by direct URL. Filters and
pagination preserve the selected filters. No customer contact data is rendered publicly.
Dates are stored using Django dates/timezone support; the MVP does not include a Jalali date picker.

## Verify

```cmd
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Production

Set DJANGO_DEBUG=0, a strong DJANGO_SECRET_KEY and exact DJANGO_ALLOWED_HOSTS.
Configure HTTPS, a production WSGI/ASGI server, backups for db.sqlite3 and media, and logging.
Ensure the process can write to the SQLite database file and its parent directory.
Run migrate and collectstatic. Serve static files and public media with your web server;
Django serves media only in debug mode. Uploads are verified raster images limited to 10 MB and 25 megapixels. New images are resized to fit 2400 × 2400 pixels, converted to WebP, and stripped of EXIF metadata.
The library is **public-only**: do not upload confidential images, facility configurations,
or private documents. Assets can be reached by their media URL even if their owning record
is unpublished. Private assets need separate storage and authorized delivery in a later phase.
Use a shared cache and reverse-proxy rate limiting for public contact forms at production scale;
the built-in cooldown is per session/process. No real products, features, customer claims,
or project content are seeded automatically.

## Language and theme

The header language button posts to Django's CSRF-protected set_language view. It preserves
current URLs and filters and stores the language in a cookie for one year. Django also honors
supported browser language preferences. English is the default when no preference is available.
Public interface copy, form labels, request feedback, and status labels support both languages.
The HTML lang and dir attributes switch between en/ltr and fa/rtl.

Write primary editorial content in English. Optional *_fa fields in Admin hold Persian
translations for products, features, specifications, projects, company information, galleries,
category/industry names, and image alt text. Missing Persian translations fall back to the
primary content. Existing records are preserved; the site does not automatically translate
content entered by editors. English and Persian sections are separated in the main Admin editors.

Inter remains the English typeface. Persian pages additionally load persian-fonts.css and
persian-type.css: Vazirmatn for reading text, technical headings, branding, navigation, forms and controls;
Noto Nastaliq Urdu for Persian display titles, directory and feature headings, and engineering activity names. Fonts are self-hosted
under static/fonts/ with their license files. The previous fonts remain as unused assets. Their SIL Open Font License files are included alongside the fonts.
No visitor requests to Google Fonts are needed. The English font pairing was informed by https://mhsheikhi.cv/. The site has an independent, light editorial layout with dedicated pages, blue panels,
turquoise accents, orange details, and pale blue-white surfaces, and the supplied transparent company mark.
Site content and components are specific to Dynamic Tech Experts.

## Company branding and reviewed content

The transparent mark is stored at static/brand/ostadan-fanavari.png, copied unchanged
from the supplied LogoT.png. CSS frames its transparent padding and displays the original
black artwork as a light mark on dark surfaces. It appears in the header, footer, homepage,
and company page.

The company profile contains reviewed English/Persian copy, capabilities, the office telephone,
and the office neighborhood from the supplied business documents. No personal identity,
banking, ownership, or correspondence files are included in public assets.
For a fresh database, run `python manage.py import_company_profile` after migrations.
The command fills empty profile fields while preserving existing editor content; all
imported text and contact information remain editable in Django Admin.

## Page architecture and progressive enhancement

The homepage is a compact introduction and directory. Product catalogs and details,
project portfolio and case studies, the company profile, engineering approach, and
contact form are separate server-rendered pages. No homepage section navigation or
simulated application dashboards are used. The engineering page describes a proposed
collaboration framework, not certifications, performance claims, or customer endorsements.

Shared design tokens and components live in static/css/site.css. Optional vanilla JavaScript
in static/js/site.js adds a keyboard-accessible mobile menu and short entry reveals.
All content and navigation remain available without JavaScript. Reveal effects respect
reduced-motion preferences and have a timeout fallback. The language switch remains a
server-side POST, preserving the current page and query parameters.

The company name is Dynamic Tech Experts in English and استادان فناوری پویا in Persian.
A data migration corrects earlier default branding while preserving customized company copy.

## Horizon SCADA product catalog

The reviewed bilingual product catalog is available at /products/horizon-scada/ and is
stored in the regular product models. It includes 10 capabilities, 11 specification entries,
4 editorial sections and 5 FAQs. Sections and FAQs can be edited inline in Product Admin;
publication flags also apply to those entries. Future products use the same templates.

For a fresh database, run `python manage.py import_horizon_catalog` after migrations.
Re-running the command updates the supplied catalog entries, so export or preserve intentional
editorial changes before doing so. Additional editor-created entries are not deleted.
The source copy lives in apps/products/data/horizon_scada.json. The internal review record
is docs/horizon-catalog-evidence.md; it is not served by any public route.

The catalog layout includes short section navigation, native accessible FAQ disclosures,
and a print command that expands the FAQs for print, then restores their previous state.
Product details continue to work without JavaScript. No customer facility imagery or
private installation information has been copied into the public catalog.

## Leadership and engineering copy

Leadership attribution has been removed from the public site and company profile. The business phone
is +98 917 846 2012. Migrations update the existing singleton profile; a fresh profile can
be initialized using import_company_profile.

The Engineering page uses structured bilingual editorial content in
apps/company/engineering_copy.py. It presents the approved six-activity table: problem/process analysis, requirements analysis,
solution design, incremental development, verification/release, and operation/improvement.
Each activity has an action description and useful output in English and Persian, with a
responsive layout and a note explaining feedback between iterations;
there are no certification or quantified service-level claims.

## Abadeh wastewater project

The public portfolio includes /projects/abadeh-wastewater-treatment-plant/ in English and
Persian, linked to Horizon SCADA and the Water and wastewater industry. Run
`python manage.py import_abadeh_project` after migrations to reproduce the reviewed entry.
The importer creates the Horizon catalog only if its product does not already exist.
The project is in progress; commissioning dates and performance figures have not been supplied.
A project may leave its internal customer relation empty until the contracting organization
is confirmed. The facility is not automatically treated as the legal customer.

## Light and dark appearance

The current palette uses cool neutral light surfaces and deep navy dark surfaces,
with blue primary actions and teal accents. Readable light/dark variants use semantic CSS tokens for page,
card, form, table, catalog, text, border, and panel colors.

A localized header button switches light/dark mode and saves the choice under dte-theme
in localStorage. The initial mode follows the system preference when no explicit choice
exists. The local theme.js runs before the stylesheets to avoid an incorrect initial paint;
it also handles system changes, cross-tab preference changes, and unavailable storage.
The site remains usable with JavaScript disabled. Print styles use light document colors.

Persian typography roles are scoped to html[lang="fa"] and their stylesheets are loaded
only for Persian pages. Persian font-face declarations cover Arabic/Persian glyphs;
Latin product names and technical notation retain Inter. Font sizes and line heights
are tuned separately for headings, long paragraphs, interface text, and narrow screens.


## Project records and the expanded Horizon catalog

Projects support optional verified progress, a private-by-default amount with explicit
public display control, and a currency (IRR, toman, USD, EUR). Completed projects display
100%; in-progress projects only display a percentage when one has been supplied.
Project parties are edited inline: client, contractor, consultant and principal client,
with approved English/Persian public names and individual publication switches. Internal
organization names are never exposed through the party relation. The existing cover and
ordered image gallery are editable from the same project screen.

Horizon has nine technical chapters and five HTML diagrams covering hierarchy, alarm
transitions, historical calculations, access evaluation and multi-site integration.
Product sections accept optional library images and bilingual captions for reviewed
application screenshots. Source and publication boundaries are recorded in
`docs/horizon-catalog-evidence.md`. Run `python manage.py import_horizon_catalog` and
`python manage.py import_abadeh_project` to update the bundled bilingual content.


## Motion and phone interactions

The background renderer in `static/js/ambient.js` draws pointer-responsive, deforming
3D contours in blue and teal. Home and About receive prominent contours, while other
routes use quieter variations. A second smaller form balances desktop compositions.
Phones render just one background contour slightly above viewport center with no scroll offset or
reserved hero space. It is more visible on Home and subtler on other routes. Secondary
desktop contours use separate light/dark intensities. The
renderer caps pixel ratio and frame rate, suspends on hidden pages, cancels pending
frames on page exit, and draws a still composition for prefers-reduced-motion.
No animation button or stored animation setting is used. There is no live operational
data, tracking, external rendering library, or network dependency in the effect.

Theme controls are icon-only with localized accessible names. The language switch is
an outlined button, and the company mark has a soft hover glow. The primary contact
action moves into the navigation menu on phones. The interaction layer retains reading
progress, active catalog navigation, back-to-top and native-dialog image enlargement.

Color roles use semantic light/dark tokens; the approach follows established surface,
text and accent separation described by Material and Atlassian design systems:
- https://m3.material.io/styles/color/the-color-system
- https://atlassian.design/foundations/color/color-palette

The light theme uses #f5f8fc backgrounds, #12243b text, #1763ce primary actions and
#087d86 accents. Dark uses #080f1c backgrounds, #edf5ff text, #76afff primary actions
and #63d4dd accents. These are our palette choices, not a claim of a universally
best or most popular theme.

Phone navigation, compact mobile catalog section selection, forms, typography and tables have
dedicated styles. Personal leadership fields and seed values were removed in company
migration 0007. The existing content and forms remain usable without JavaScript.


Mobile navigation uses a compact 65px row with the company mark, icon menu, theme
switch and language button. A native modal drawer opens from the inline-start edge
(right for Persian, left for English), traps focus, closes with Escape or the backdrop,
and restores focus to the menu control. Desktop navigation is restored at the breakpoint.
The main contact action is available inside the drawer. Without JavaScript, normal
navigation remains in the document flow.


The compact menu control sits at the inline-start edge, matching the drawer (right in
Persian, left in English). Content cards and note panels use theme-aware translucent
surfaces with a 10px backdrop blur; technical tables retain readable header contrast.
On phones the contour radius is 29% of the viewport width (capped at 124px), its center
is at 44% of viewport height, and Home has a brighter glow than content routes.


On phones the product catalog uses a 62px sticky section selector instead of a
horizontal scrolling ribbon. Options are derived from the existing section links;
selection jumps to the heading with clearance below the control. Scroll tracking
accounts for sticky control height and document scroll padding. Desktop retains its
section links; without JavaScript the phone links wrap in normal flow.


Phone contour rendering now follows device pixel density up to 3x (desktop up to 2x),
with 48 mobile contour rings and 112 samples per ring. The sharp foreground strokes
remain separate from the soft bloom passes. The existing mobile frame-rate limit and
hidden-page/reduced-motion handling remain in effect. This replaces the original 1.25x
phone bitmap cap, which could look soft on Retina screens.
