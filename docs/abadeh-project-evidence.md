# Abadeh project publication

The user explicitly requested adding the Abadeh wastewater treatment project to the public
portfolio. The supplied company letter (Messages/01 Saabniroo Afta.pdf in the company folder)
identifies Dynamic Tech Experts as the developer of the Abadeh wastewater SCADA software.
The Horizon checkout supports the descriptions of the process views and application capabilities.

The entry describes software development and is marked in progress. No commissioning date,
completion date, capacity, performance result, certification, or customer endorsement is asserted.
The confirmed contracting legal entity has not been established, so the customer relation is
left empty rather than treating the facility name or the recipient of a letter as a legal client.
No correspondence, personal data, operating diagrams, or facility images are published.

Run `python manage.py import_abadeh_project` to reproduce the public English/Persian record,
industry classification, and relationship to Horizon. The importer preserves a subsequently
assigned customer and does not remove additional product links or gallery records.


## Project metadata extension — 2026-10-28

ProjectParty records support client, contractor, consultant, and principal client. An
optional protected organization relation is internal; only an explicitly published public
name is rendered. Several parties may hold the same role. Abadeh has no seeded party names
because those legal identities have not been verified.

Project value and currency are optional. The public page only renders a value when
show_contract_value is enabled. Progress is nullable, 0–100; completed projects display 100.
Abadeh remains in progress with no invented percentage or value. Its existing cover and
ordered gallery remain available, with bilingual captions. The importer preserves later
status and contractual metadata. The hierarchy example is educational rather than an
extraction from a production database.


## Confirmed project board — 2026-10-28

The user supplied `codex-clipboard-00a875ee-9ab5-4873-bcf1-8cc66f13ad3e.png`
and explicitly requested populating the public project record from it. This supersedes
the earlier absence of verified party names:

- Employer/client: Fars Water and Wastewater Co. / شرکت آب و فاضلاب استان فارس
- Plant contractor: Mahab Ghods–Sabniroo Joint Venture / مشارکت مهاب قدس–ساب نیرو
- Consultant: Tehran Sahab Consulting Engineers / شرکت مهندسین مشاور تهران سحاب
- Financier: Islamic Development Bank / بانک توسعه اسلامی
- Software/SCADA developer: Dynamic Tech Experts / استادان فناوری پویا,
  explicitly confirmed by the user as distinct from the plant contractor.

The board identifies the plant project as DBO with design, procurement, construction,
testing, commissioning and operation. That broader scope is not attributed to Dynamic
Tech Experts. No separate principal-client organization is identified, so the public
field is labelled Not specified rather than duplicating or inferring a party. The
internal customer FK remains unset because the board does not establish the direct
contracting organization for the software engagement. Price, percentage, dates and
endorsements remain unasserted. Party upserts are repeatable and preserve custom parties.


## User correction of contractual roles

The user explicitly corrected the interpretation of the board for the software engagement:
Saabniroo is the client, Fars Water and Wastewater Co. is the principal client, and
Dynamic Tech Experts is the contractor as well as SCADA developer. These roles supersede
the earlier board-based assignment in the public entry and importer. The former client
and contractor records are unpublished by exact role/name, with custom entries preserved.
The heading is Contractor / پیمانکار, without extending the software scope to the entire
plant. Consultant and financier remain as previously confirmed for the wider project.
