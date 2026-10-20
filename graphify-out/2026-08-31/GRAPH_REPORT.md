# Graph Report - app  (2026-08-30)

## Corpus Check
- 121 files · ~230,619 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1214 nodes · 1948 edges · 135 communities (71 shown, 64 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7ff2a485`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- devDependencies
- SupabaseCollection
- inventory_routes.py
- routes_module.py
- tracking_module.py
- RoutesPage.js
- ServiceOrdersPage.js
- InventoryPage.js
- laudo_generator.py
- TelecontrolScraper
- serviceWorkerRegistration.js
- App.js
- use-toast.js
- post
- accordion.jsx
- BaseModel
- form.jsx
- components.json
- cn
- menubar.jsx
- Guia de Migração — MasterMaq Sync Hub
- manuais_module.py
- printingService.js
- date-fns
- manifest.json
- migration_script.py
- create_external_os
- users_module.py
- assinafy_service.py
- button.jsx
- mark_all_notifications_read
- card.jsx
- command.jsx
- context-menu.jsx
- whatsapp_module.py
- migrate_to_supabase.py
- _run_sync_with_health
- create_signature_link
- table.jsx
- migrate_railway.py
- breadcrumb.jsx
- drawer.jsx
- ManuaisPage.js
- navigation-menu.jsx
- sheet.jsx
- label_templates_module.py
- migrate_to_new_supabase.py
- WebpackHealthPlugin
- toggle-group.jsx
- auth.js
- mapAssets.js
- migrate_fix.py
- compilerOptions
- health-endpoints.js
- OSPublicViewPage.js
- alert.jsx
- Política de uso do Graphify neste projeto
- migration_verify.py
- CacheHeaderMiddleware
- dispatch_webhook.sh
- craco.config.js
- DashboardLayout.js
- Learn More
- watch_crons.sh
- axios
- class-variance-authority
- clsx
- cmdk
- dependencies
- embla-carousel-react
- webhook_crond.sh
- @hookform/resolvers
- html2pdf.js
- input-otp
- mammoth
- PublicSignPage.js
- @radix-ui/react-accordion
- @radix-ui/react-alert-dialog
- @radix-ui/react-aspect-ratio
- @radix-ui/react-avatar
- @radix-ui/react-checkbox
- @radix-ui/react-collapsible
- @radix-ui/react-context-menu
- @radix-ui/react-dialog
- @radix-ui/react-dropdown-menu
- @radix-ui/react-hover-card
- @radix-ui/react-label
- @radix-ui/react-menubar
- input-otp.jsx
- PRD — Mastermaq / Maq-Sync-Hub
- @radix-ui/react-progress
- @radix-ui/react-radio-group
- PublicTrackingPage.js
- @radix-ui/react-select
- qrcode
- fabric
- @radix-ui/react-slot
- @radix-ui/react-popover
- lucide-react
- @radix-ui/react-toggle-group
- @radix-ui/react-tooltip
- @radix-ui/react-tabs
- @react-google-maps/api
- @radix-ui/react-toast
- @radix-ui/react-slider
- whatsapp_send_copy
- react-scripts
- recharts
- @supabase/supabase-js
- tailwind-merge
- tailwindcss-animate
- vaul
- zod
- react-day-picker
- sonner
- README.md
- next-themes
- AsyncClient
- @radix-ui/react-toggle
- react-hook-form
- react-router-dom
- BaseModel
- delete
- get
- HTTPAuthorizationCredentials
- post
- put

## God Nodes (most connected - your core abstractions)
1. `cn()` - 67 edges
2. `useAuth()` - 22 edges
3. `SupabaseCollection` - 19 edges
4. `Button` - 16 edges
5. `Label` - 13 edges
6. `TelecontrolScraper` - 12 edges
7. `Input` - 12 edges
8. `FindCursor` - 11 edges
9. `DashboardLayout()` - 10 edges
10. `printOSLabel()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `OrderDetailOverlay()` --indirect_call--> `toast()`  [INFERRED]
  frontend/src/components/OrderDetailOverlay.js → frontend/src/hooks/use-toast.js
- `BreadcrumbSeparator()` --calls--> `cn()`  [EXTRACTED]
  frontend/src/components/ui/breadcrumb.jsx → frontend/src/lib/utils.js
- `BreadcrumbEllipsis()` --calls--> `cn()`  [EXTRACTED]
  frontend/src/components/ui/breadcrumb.jsx → frontend/src/lib/utils.js
- `CommandShortcut()` --calls--> `cn()`  [EXTRACTED]
  frontend/src/components/ui/command.jsx → frontend/src/lib/utils.js
- `ContextMenuShortcut()` --calls--> `cn()`  [EXTRACTED]
  frontend/src/components/ui/context-menu.jsx → frontend/src/lib/utils.js

## Import Cycles
- 3-file cycle: `frontend/src/components/DashboardLayout.js -> frontend/src/components/OrderDetailOverlay.js -> frontend/src/pages/ServiceOrdersPage.js -> frontend/src/components/DashboardLayout.js`

## Communities (135 total, 64 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.04
Nodes (78): api_health(), CEPResponse, check_new_external_os(), create_token(), env_check(), fetch_temp_pdf(), get_alerts_summary(), get_customer_history() (+70 more)

### Community 1 - "devDependencies"
Cohesion: 0.04
Nodes (46): autoprefixer, @babel/plugin-proposal-private-property-in-object, @craco/craco, @emergentbase/visual-edits, eslint, @eslint/js, eslint-plugin-import, eslint-plugin-jsx-a11y (+38 more)

### Community 2 - "SupabaseCollection"
Cohesion: 0.08
Nodes (17): AggCursor, FindCursor, _get_client(), _headers(), Supabase database adapter - provides MongoDB-like interface over Supabase REST…, Basic aggregation support - returns AggCursor, Mimics Motor's find cursor with chaining, Format a value for PostgREST filter (+9 more)

### Community 3 - "inventory_routes.py"
Cohesion: 0.08
Nodes (44): AsyncClient, _auth(), BatchCreate, create_batch(), create_movement(), create_product(), create_serial(), create_supplier() (+36 more)

### Community 4 - "routes_module.py"
Cohesion: 0.10
Nodes (38): _address_hash(), _build_waypoint(), cache_coords(), CacheCoordsItem, CacheCoordsRequest, compute_route(), ComputeRouteRequest, create_route() (+30 more)

### Community 5 - "tracking_module.py"
Cohesion: 0.11
Nodes (35): BreadcrumbPoint, create_share_token(), current_session(), end_tracking(), get_breadcrumbs(), get_live_position(), get_tracking_config(), GPSUpdate (+27 more)

### Community 6 - "RoutesPage.js"
Cohesion: 0.13
Nodes (10): Checkbox, PopoverContent, Slider, supabase, EXCLUDED_STATUSES, GOOGLE_MAPS_LIBRARIES, IMPORTANT: do NOT depend on `orders` directly — its reference changes on, IMPORTANT: do NOT depend on `orders` — its reference changes on every (+2 more)

### Community 7 - "ServiceOrdersPage.js"
Cohesion: 0.12
Nodes (20): LaudoModal(), PHOTO_LABELS, IMPORTANT: the OS PUT (step 2) is ADDITIVE — we only send a field if the, RECALL_PHOTO_LABELS, OrderDetailOverlay(), TabsContent, TabsList, TabsTrigger (+12 more)

### Community 8 - "InventoryPage.js"
Cohesion: 0.12
Nodes (12): DialogContent, DialogDescription, DialogHeader(), DialogOverlay, DialogTitle, DEFAULT_CATEGORIES, ENTRY_REASONS, EXIT_REASONS (+4 more)

### Community 9 - "laudo_generator.py"
Cohesion: 0.10
Nodes (27): _decode_base64_image(), generate_laudo_from_template(), generate_recall_laudo(), _get_month_name(), _make_blank_jpeg(), Laudo Generator - Template-based approach Opens the real DOCX template and…, Replace status cell text with clean formatting (white background, black text).…, Replace serial number in cell, targeting the bold run at the end. (+19 more)

### Community 10 - "TelecontrolScraper"
Cohesion: 0.09
Nodes (19): Script para rodar o sync do Telecontrol manualmente, cobrindo um período…, Run sync for both Hisense and HQ Telecontrol, Run sync periodically every SYNC_INTERVAL_MINUTES, run_sync(), scheduler(), extract_brand_from_description(), Internal sync implementation, Close browser instance safely (+11 more)

### Community 12 - "App.js"
Cohesion: 0.15
Nodes (6): App(), Toaster(), AuthContext, AuthProvider(), failedQueue, root

### Community 13 - "use-toast.js"
Cohesion: 0.16
Nodes (18): Toast, ToastAction, ToastClose, ToastDescription, ToastTitle, toastVariants, ToastViewport, Toaster() (+10 more)

### Community 14 - "post"
Cohesion: 0.08
Nodes (28): create_os_share_token(), fire_test_webhook(), generate_laudo_word(), get_photos_status(), increment_print_count(), LaudoData, migrate_fix_aguardando_status(), migrate_statuses() (+20 more)

### Community 15 - "accordion.jsx"
Cohesion: 0.50
Nodes (3): AccordionContent, AccordionItem, AccordionTrigger

### Community 16 - "BaseModel"
Cohesion: 0.13
Nodes (20): create_service_order(), force_resync(), login(), LoginRequest, LoginResponse, Notification, public_signature_submit(), PublicSignSubmit (+12 more)

### Community 17 - "form.jsx"
Cohesion: 0.06
Nodes (32): react, Carousel, CarouselContent, CarouselContext, CarouselItem, CarouselNext, CarouselPrevious, useCarousel() (+24 more)

### Community 18 - "components.json"
Cohesion: 0.11
Nodes (17): aliases, components, hooks, lib, ui, utils, iconLibrary, rsc (+9 more)

### Community 19 - "cn"
Cohesion: 0.08
Nodes (30): AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter(), AlertDialogHeader(), AlertDialogOverlay, AlertDialogTitle (+22 more)

### Community 20 - "menubar.jsx"
Cohesion: 0.12
Nodes (11): Menubar, MenubarCheckboxItem, MenubarContent, MenubarItem, MenubarLabel, MenubarRadioItem, MenubarSeparator, MenubarShortcut() (+3 more)

### Community 21 - "Guia de Migração — MasterMaq Sync Hub"
Cohesion: 0.12
Nodes (15): 1️⃣ Visão geral do stack, 2️⃣ Passo a passo, 3️⃣ Arquitetura — como orientar, 4️⃣ Otimizações críticas ativas (NÃO reverter!), 5️⃣ Contas de teste, 6️⃣ Checklist final antes de entregar, 7️⃣ Troubleshooting, A. Substituir o /app (+7 more)

### Community 22 - "manuais_module.py"
Cohesion: 0.15
Nodes (15): _convert_pptx_to_pdf(), _find_soffice(), get_object(), init_storage(), _pdf_page_count(), put_object(), APIRouter, Manuais Module - File management for technical manuals Upload, organize by… (+7 more)

### Community 23 - "printingService.js"
Cohesion: 0.19
Nodes (20): LabelTemplatesPage(), GARANTIA_SUBTYPES, normalizeServiceType(), OrderDetailModal(), OS_STATUSES, SERVICE_TYPES, ServiceOrdersPage(), baseStyles() (+12 more)

### Community 25 - "manifest.json"
Cohesion: 0.14
Nodes (13): background_color, categories, description, display, icons, lang, name, orientation (+5 more)

### Community 26 - "migration_script.py"
Cohesion: 0.22
Nodes (12): fetch_os_data(), login(), map_to_schema(), parse_visit_fee(), Migration script - Fetches service orders from the old Mastermaq system and…, Save progress to JSON file for monitoring, Parse 'R$ 80,00' to 80.0, Login to the old system (+4 more)

### Community 27 - "create_external_os"
Cohesion: 0.15
Nodes (8): create_external_os(), ExternalOS, Lightweight in-memory cache with TTL., OS received from external website/system, Send WhatsApp text message to Mastermaq office number., Create OS from external website/system. Uses the same numbering pattern as…, send_wa_notification(), SimpleCache

### Community 28 - "users_module.py"
Cohesion: 0.19
Nodes (11): hash_password(), BaseModel, Users module — RBAC (Admin vs Technician) with bcrypt password hashing.…, Register /api/users routes. Admin-only for write operations., Ensure the legacy/master admin exists and password matches env., seed_admin(), setup_users_routes(), UserCreate (+3 more)

### Community 29 - "assinafy_service.py"
Cohesion: 0.17
Nodes (11): create_assignment(), create_signer(), generate_os_pdf(), get_document_status(), Assinafy Digital Signature Service Handles PDF generation and Assinafy API…, Upload a PDF document to Assinafy and return the document data, Create a signer in Assinafy, Create a virtual assignment for the document (+3 more)

### Community 30 - "button.jsx"
Cohesion: 0.18
Nodes (16): DashboardLayout(), NotificationsPanel(), Button, DialogFooter(), Input, Label, labelVariants, Switch (+8 more)

### Community 31 - "mark_all_notifications_read"
Cohesion: 0.50
Nodes (5): delete_service_order(), mark_all_notifications_read(), mark_notification_read(), delete, put

### Community 32 - "card.jsx"
Cohesion: 0.28
Nodes (6): Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle

### Community 33 - "command.jsx"
Cohesion: 0.20
Nodes (8): Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator, CommandShortcut()

### Community 34 - "context-menu.jsx"
Cohesion: 0.20
Nodes (9): ContextMenuCheckboxItem, ContextMenuContent, ContextMenuItem, ContextMenuLabel, ContextMenuRadioItem, ContextMenuSeparator, ContextMenuShortcut(), ContextMenuSubContent (+1 more)

### Community 35 - "whatsapp_module.py"
Cohesion: 0.22
Nodes (8): get_saudacao(), _get_shared_client(), APIRouter, AsyncClient, WhatsApp Business API Module Handles configuration, message sending,…, Dynamic greeting based on time of day (Brasilia timezone UTC-3), Register WhatsApp Business API routes, setup_whatsapp_routes()

### Community 36 - "migrate_to_supabase.py"
Cohesion: 0.31
Nodes (8): clean_doc(), insert_batch(), main(), migrate_collection(), Migration script: MongoDB → Supabase (PostgreSQL via REST API) Exports all data…, Remove MongoDB _id and convert non-serializable types, Insert a batch of rows into Supabase via REST API, Migrate a MongoDB collection to a Supabase table

### Community 37 - "_run_sync_with_health"
Cohesion: 0.14
Nodes (14): _load_health_from_db(), _persist_health(), Download Playwright chromium at runtime if missing. Cloud Build cannot fetch…, Auto-migrate on startup: source names and status normalization, Start background auto-sync loop for Telecontrol HISENSE only. HQ is NOT auto-…, Background task that flips a scraper to `down` when its last run is stale…, Run scraper sync, update health metrics, and trigger auto-resync on recovery.…, _run_sync_with_health() (+6 more)

### Community 38 - "create_signature_link"
Cohesion: 0.33
Nodes (6): create_signature_link(), Gera um link público para o cliente assinar a OS pelo próprio celular., Save laudo draft data to database for persistence. ADDITIVE save: only fields…, save_laudo_data(), SignatureLinkCreate, Request

### Community 39 - "table.jsx"
Cohesion: 0.22
Nodes (8): Table, TableBody, TableCaption, TableCell, TableFooter, TableHead, TableHeader, TableRow

### Community 40 - "migrate_railway.py"
Cohesion: 0.39
Nodes (7): clear_table(), get_supabase_count(), insert_batch(), main(), normalize(), Migration: Railway MongoDB (production) → Supabase (PostgreSQL) Clears test…, Delete all rows from a Supabase table

### Community 41 - "breadcrumb.jsx"
Cohesion: 0.25
Nodes (7): Breadcrumb, BreadcrumbEllipsis(), BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator()

### Community 42 - "drawer.jsx"
Cohesion: 0.25
Nodes (6): DrawerContent, DrawerDescription, DrawerFooter(), DrawerHeader(), DrawerOverlay, DrawerTitle

### Community 43 - "ManuaisPage.js"
Cohesion: 0.17
Nodes (14): Badge(), badgeVariants, SelectContent, SelectItem, SelectLabel, SelectScrollDownButton, SelectScrollUpButton, SelectSeparator (+6 more)

### Community 44 - "navigation-menu.jsx"
Cohesion: 0.25
Nodes (7): NavigationMenu, NavigationMenuContent, NavigationMenuIndicator, NavigationMenuList, NavigationMenuTrigger, navigationMenuTriggerStyle, NavigationMenuViewport

### Community 45 - "sheet.jsx"
Cohesion: 0.25
Nodes (7): SheetContent, SheetDescription, SheetFooter(), SheetHeader(), SheetOverlay, SheetTitle, sheetVariants

### Community 46 - "label_templates_module.py"
Cohesion: 0.33
Nodes (4): LabelTemplate, LabelTemplateIn, BaseModel, Label Templates module — CRUD para templates de adesivos térmicos. Armazena…

### Community 47 - "migrate_to_new_supabase.py"
Cohesion: 0.38
Nodes (6): insert_batch(), main(), Supabase Database Migration Script =================================== Creates…, Read CSV and return list of dicts, Insert rows in batches via Supabase REST API, read_csv()

### Community 49 - "toggle-group.jsx"
Cohesion: 0.33
Nodes (5): ToggleGroup, ToggleGroupContext, ToggleGroupItem, Toggle, toggleVariants

### Community 50 - "auth.js"
Cohesion: 0.29
Nodes (4): LOGIN, LOGOUT, REGISTER, HOME

### Community 51 - "mapAssets.js"
Cohesion: 0.33
Nodes (5): createMotoIcon(), MAP_STYLE, MOTO_SVG, ROUTE_POLYLINE_STYLES, STOP_COLORS

### Community 52 - "migrate_fix.py"
Cohesion: 0.47
Nodes (5): insert_batch(), main(), normalize(), Fix migration: insert missing service_orders and sync_logs with normalized keys, Ensure doc has exactly the specified columns, with None for missing

### Community 53 - "compilerOptions"
Cohesion: 0.33
Nodes (5): compilerOptions, baseUrl, paths, include, src

### Community 54 - "health-endpoints.js"
Cohesion: 0.47
Nodes (5): formatBytes(), formatDuration(), os, SERVER_START_TIME, setupHealthEndpoints()

### Community 56 - "alert.jsx"
Cohesion: 0.40
Nodes (4): Alert, AlertDescription, AlertTitle, alertVariants

### Community 57 - "Política de uso do Graphify neste projeto"
Cohesion: 0.33
Nodes (5): Comandos úteis, Política de uso do Graphify neste projeto, Quando NÃO USAR o grafo (ler arquivo direto), Quando USAR o grafo (`graphify query/path/explain`), Ruído já excluído (via `/app/.graphifyignore`)

### Community 58 - "migration_verify.py"
Cohesion: 0.67
Nodes (3): capture_fields(), Verify OS data by loading in browser form (the reliable method) vs what the…, verify()

### Community 59 - "CacheHeaderMiddleware"
Cohesion: 0.50
Nodes (3): CacheHeaderMiddleware, Cache policy: - Live data (service-orders, routes, notifications, tracking,…, BaseHTTPMiddleware

### Community 61 - "craco.config.js"
Cohesion: 0.50
Nodes (3): config, path, webpackConfig

### Community 62 - "DashboardLayout.js"
Cohesion: 0.17
Nodes (12): menuItems, DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuRadioItem, DropdownMenuSeparator, DropdownMenuShortcut() (+4 more)

### Community 63 - "Learn More"
Cohesion: 0.14
Nodes (13): Advanced Configuration, Analyzing the Bundle Size, Available Scripts, Code Splitting, Deployment, Getting Started with Create React App, Learn More, Making a Progressive Web App (+5 more)

### Community 69 - "dependencies"
Cohesion: 0.13
Nodes (15): cra-template, dependencies, cra-template, @radix-ui/react-navigation-menu, @radix-ui/react-scroll-area, @radix-ui/react-separator, @radix-ui/react-switch, react-dom (+7 more)

### Community 89 - "input-otp.jsx"
Cohesion: 0.40
Nodes (4): InputOTP, InputOTPGroup, InputOTPSeparator, InputOTPSlot

### Community 90 - "PRD — Mastermaq / Maq-Sync-Hub"
Cohesion: 0.12
Nodes (16): 1. Migração do repositório (20/07), 2. Bug "Dados para Laudo apagam de um dia pro outro" (20/07), 3. Bug "somente 1ª imagem em todas" no laudo DOCX (21-31/07), 4. Scraper Telecontrol blindado (31/07), 5. Bug "fotos apagam ao reabrir OS" (31/07), 6. Aba "OSs Atrasadas" não renderizava (ServiceOrdersPage.js:1196), 7. Campainha tocando ao mudar de página (DashboardLayout.js:200), 8. Adesivo personalizado imprimindo torto / vários por impressão (LabelTemplatesPage.js + printingService.js) (+8 more)

### Community 93 - "PublicTrackingPage.js"
Cohesion: 0.67
Nodes (3): GOOGLE_MAPS_LIBRARIES, haversine(), PublicTrackingPage()

### Community 106 - "whatsapp_send_copy"
Cohesion: 0.67
Nodes (3): Upload the PDF generated on the frontend to Meta Media API, then send it as a…, SendCopyRequest, whatsapp_send_copy()

## Knowledge Gaps
- **318 isolated node(s):** `1. Migração do repositório (20/07)`, `2. Bug "Dados para Laudo apagam de um dia pro outro" (20/07)`, `3. Bug "somente 1ª imagem em todas" no laudo DOCX (21-31/07)`, `4. Scraper Telecontrol blindado (31/07)`, `5. Bug "fotos apagam ao reabrir OS" (31/07)` (+313 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **64 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `dependencies` connect `dependencies` to `devDependencies`, `form.jsx`, `date-fns`, `axios`, `class-variance-authority`, `clsx`, `cmdk`, `embla-carousel-react`, `@hookform/resolvers`, `html2pdf.js`, `input-otp`, `mammoth`, `@radix-ui/react-accordion`, `@radix-ui/react-alert-dialog`, `@radix-ui/react-aspect-ratio`, `@radix-ui/react-avatar`, `@radix-ui/react-checkbox`, `@radix-ui/react-collapsible`, `@radix-ui/react-context-menu`, `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-hover-card`, `@radix-ui/react-label`, `@radix-ui/react-menubar`, `@radix-ui/react-progress`, `@radix-ui/react-radio-group`, `@radix-ui/react-select`, `qrcode`, `fabric`, `@radix-ui/react-slot`, `@radix-ui/react-popover`, `lucide-react`, `@radix-ui/react-toggle-group`, `@radix-ui/react-tooltip`, `@radix-ui/react-tabs`, `@react-google-maps/api`, `@radix-ui/react-toast`, `@radix-ui/react-slider`, `react-scripts`, `recharts`, `@supabase/supabase-js`, `tailwind-merge`, `tailwindcss-animate`, `vaul`, `zod`, `react-day-picker`, `sonner`, `next-themes`, `@radix-ui/react-toggle`, `react-hook-form`, `react-router-dom`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `react` connect `form.jsx` to `use-toast.js`, `dependencies`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `cn()` connect `cn` to `RoutesPage.js`, `ServiceOrdersPage.js`, `InventoryPage.js`, `use-toast.js`, `accordion.jsx`, `form.jsx`, `menubar.jsx`, `button.jsx`, `card.jsx`, `command.jsx`, `context-menu.jsx`, `table.jsx`, `breadcrumb.jsx`, `drawer.jsx`, `ManuaisPage.js`, `navigation-menu.jsx`, `sheet.jsx`, `toggle-group.jsx`, `alert.jsx`, `DashboardLayout.js`, `input-otp.jsx`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **What connects `1. Migração do repositório (20/07)`, `2. Bug "Dados para Laudo apagam de um dia pro outro" (20/07)`, `3. Bug "somente 1ª imagem em todas" no laudo DOCX (21-31/07)` to the rest of the system?**
  _318 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `server.py` be split into smaller, more focused modules?**
  _Cohesion score 0.039240506329113925 - nodes in this community are weakly interconnected._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.0425531914893617 - nodes in this community are weakly interconnected._
- **Should `SupabaseCollection` be split into smaller, more focused modules?**
  _Cohesion score 0.08233117483811286 - nodes in this community are weakly interconnected._