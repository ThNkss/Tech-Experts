# Horizon SCADA catalog — editorial evidence

Reviewed source: `D:/Useful_Documents/Projects/Horizon` (read-only review).
The catalog describes code present in that checkout; it is not a claim of field validation,
certification, measured capacity, guaranteed latency, or compatibility with every PLC.
No production data, credentials, facility images, customer names, endpoints, or site diagrams
were copied into public assets. The existing images inspected were facility backgrounds,
not neutral product screenshots.

| Catalog subject | Reviewed implementation |
|---|---|
| Hierarchical process model | hierarchy/models.py; hmi/services/pages.py |
| Image/P&ID views and placement editing | hmi/views/hmi.py; hmi/views/edit.py; hmi/models.py |
| Tag roles, types, units, limits and commands | tags/models.py; tags/urls.py; agent/opc_agent.py |
| OPC UA acquisition, writes and configuration | agent/opc_agent.py |
| Local measurement queue and replay | agent/measurement_buffer.py; agent/opc_agent.py |
| Live updates scoped to the user | Horizon/consumers.py |
| Archive profiles and history | tags/models.py; tags/services/archive_policy.py |
| HDA statistics and flow volume | tags/services/hda_report.py |
| HDA CSV/Excel export | tags/api/report_views.py; tags/api/urls.py |
| Alarm lifecycle and guidance | alarms/models.py; alarms/urls.py; alarms/tests_lifecycle.py |
| Alarm analysis and Excel exports | alarms/views/reports.py |
| Equipment properties, runtime, service records | equipment/models.py; equipment/urls.py |
| Personnel roles, scope and overrides | people/models.py; people/services/access.py |
| Local and AD sign-in workflows | people/urls.py; people/views/person.py |
| Audit records, review and export | audit/models.py; audit/views/audit.py |
| Water/wastewater process areas | core/urls.py; core/views/process.py |

Editorial content is stored in apps/products/data/horizon_scada.json and imported through
`python manage.py import_horizon_catalog`. The command is transactional and updates existing
catalog rows by stable lookup values; it does not remove additional editor-created entries.
Re-running it replaces the supplied copy for its matching entries. Subsequent editorial edits
can be made through Django Admin without changing templates.

Deliberately omitted: invented version/release dates, hardware minimums, benchmarks,
certifications, universal protocol support, autonomous safety/control claims, predictive
maintenance, named customer endorsements, and installation-specific screenshots.


## Expanded catalog review — 2026-10-28

The new catalog has six summary capabilities and nine detailed chapters, with five
selectable, accessible HTML figures. Figures describe the implementation and are not
screenshots of an operating installation. The Abadeh path is explicitly labelled as an
illustrative configuration; it is not an assertion about actual equipment/tag identifiers.

Additional source evidence:

- `hmi/services/image_layout.py`: descendant candidates derive from the hierarchy.
- `hmi/views/node_update.py`: candidates, class symbols, state engines and placement data.
- `core/static/assets/js/hmi_editor.js`: pointer-driven placement editor.
- `equipment/models.py`: class/property structure, run events, cached hours, service records.
- `alarms/services/alarms.py`: Active resets acknowledgement; Return clears active;
  Ack sets acknowledgement; Shelve/Suppress flags and events remain separate.
- `alarms/models.py:get_state_from_flags`: inactive+acknowledged is Return;
  inactive+unacknowledged is Normal. The diagram includes return-before-acknowledgement
  rather than presenting a generic ISA state machine as an exact implementation.
- `alarms/views/reports.py`: frequency, duration, response time, standing alarms,
  shelving/suppression, flood analysis and priority distribution, with Excel exports.
- `tags/services/hda_report.py`: per-tag configuration and supported function set.
- `tags/api/utils.py`: temporal integration excludes excessive gaps; volume validates
  flow units; quality functions return unavailable/unknown because quality is not persisted.
- `tags/api/urls.py`, `tags/api/report_views.py`: CSV/XLSX reporting routes.
- `tags/services/hda_export_audit.py`: export audit handling.
- `tags/models.py:TagCommand`: creator, schedule, states, attempts, errors and completion.
- `people/services/access.py`: global deny precedence; role plus active scopes;
  scoped grants and denials; separate superuser bypass.
- `people/services/permission_conditions.py`: validity and IP conditions.
- `people/services/access.py:_has_role_permission`: configured role operating-time window.
- `integrations/models.py`, `integrations/authentication.py`: agent tied to a site;
  certificate identity and fingerprint verification when mTLS is configured.
- `people/services/ad_tls.py`: certificate-aware directory TLS connection.
- `agent/measurement_buffer.py`, `agent/opc_agent.py`: local buffering/replay and field interface.

Standards context was checked against primary ISA pages:
- https://www.isa.org/standards-and-publications/isa-standards/isa-18-series-of-standards
- https://www.isa.org/standards-and-publications/isa-standards/isa-95-standard

ISA-18.2 concerns alarm-system management; ISA-95 concerns enterprise/control integration
and equipment modelling. Neither the source review nor this catalog proves certified
compliance. Security copy identifies implemented mechanisms and configuration dependencies,
not an unqualified assurance or an independent penetration-test result.

Live capture attempt: the existing Chrome window was detected with title “Horizon — افق”.
Computer Use stopped because it could not establish the current browser URL reliably.
No further UI input was issued after that stop. No live screenshots were captured or
published in this edition. ProductSection now supports an optional screenshot and bilingual
caption, and existing product/project galleries support additional approved raster images.

The importer retires the previous bundled features/FAQs/sections, removes obsolete bundled
specification names, and preserves additional administrator-authored entries. Historical
copy remains unpublished where the model supports publication. A SQLite backup was made
before schema/data changes in the ignored backups/ directory.
