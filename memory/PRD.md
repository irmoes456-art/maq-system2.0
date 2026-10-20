# PRD — Mastermaq / Maq-Sync-Hub

## Sessão atual (20-31/07/2026)

### 1. Migração do repositório (20/07)
- Repo `fernandodo2027-rgb/maq-sync-hub` clonado sobre /app
- Backend + frontend deps instaladas; Playwright Chromium em `/root/.cache/ms-playwright`
- Todas as 28 chaves de `backend/.env` presentes; `REACT_APP_BACKEND_URL` corrigido
- Usuário Invisacook recriado (Mongo local reseta a cada migração)
- Todas as 13 políticas de otimização de saída Supabase auditadas e íntegras
- OS `INV-00001` (teste) removida; `invisacook_seq` zerado

### 2. Bug "Dados para Laudo apagam de um dia pro outro" (20/07)
- **Photo PUT aditivo** (`LaudoModal.js runLaudoSave` + `saveDraft`): só envia `photo_i` se `images[i]` não for vazio
- **Autosave gated por flags reais** (`draftFetched && photosFetched`): substitui `setTimeout(300)`
- **Server-side photo guard** (`PUT /service-orders/{n}`): recusa `photo_i=""` se existe foto no banco, exceto com `clear_photos:[i]` explícito

### 3. Bug "somente 1ª imagem em todas" no laudo DOCX (21-31/07)
- **Hisense** (`laudo_generator.py`): user confirmou que Hisense está OK — apenas fotos órfãs do template. Não mexer no PHOTO_SLOTS.
- **Mastermaq** (`laudo_mastermaq_generator.py`): reescrito para 4 slots distintos
  - Antes: 1 foto (índice 7) copiada em image1/2/3 → todos os slots iguais
  - Depois: patch dinâmico do XML — 2ª ocorrência de `rId7` vira `rId200` + novo relationship + arquivo `image_foto2.jpeg`
  - Mapping: modal FOTO 1 → template FOTO 1 (esq); modal FOTO 2 → template FOTO 2 (dir); modal FOTO 7 → template FOTO 3 (Defeito); modal FOTO 4 → template FOTO 4 (Elétrica)
  - Validado visualmente com 4 cores distintas

### 4. Scraper Telecontrol blindado (31/07)
Bug raiz: 3 falhas em cascata que se escondiam mutuamente:
- `login()` retornava True se URL não continha "erro"
- `except Exception: break` na paginação silenciava tudo
- `success=True` no final independente de falhas parciais

Correções aplicadas:
- `login()`: valida URL de página logada + chama JS `login()` direto + captura `#msgErro` + retry 2×
- Paginação: retry 3× com backoff, `networkidle` 15→30s, `raise` em erro real
- `sync_orders`: retry login+fetch 2× cada, campo `degraded`, success só se ambos OK
- `_run_sync_with_health`: detecção de volume anômalo (<20% da média das últimas 5 execuções)
- Watchdog interno (`_scraper_watchdog`): task async no boot, marca `down` se sync > 3× interval
- `/api/scrapers/health` retorna `overall_message` ("Scraper Hisense falhou")
- Badge no `DashboardLayout` mostra mensagem específica

**Bug real exposto**: credenciais Hisense do `.env` (`19955560000128`/`Thami2007`) foram rejeitadas pelo Telecontrol com "Login ou senha inválidos". User precisa atualizar `TELECONTROL_PASSWORD` e rodar `POST /api/scrapers/hisense/resync?days=60` pra recuperar as 4 OSs perdidas.

### 5. Bug "fotos apagam ao reabrir OS" (31/07)
Achado no `useEffect` merge-only sync do `ServiceOrdersPage.js` (linha 1755):
```diff
- if (k.startsWith('photo_')) continue;
```
O guard `isPrevEmpty` já protege contra sobrescrever fotos em upload local. O `continue` bloqueava o merge legítimo quando handleOrderClick abria o modal com snapshot da lista (sem fotos) e o GET `?include_photos=1` chegava depois em paralelo. Removida a linha — fotos agora são hidratadas normalmente.

## Backlog
- Canal externo de alerta SMS para scraper (item 3.2 do plano do scraper)
- Simulação de queda de rede via mock
- README de manutenção do scraper
- Documentação de referência

## Sessão 30/08/2026 — 3 fixes de UX

### 6. Aba "OSs Atrasadas" não renderizava (ServiceOrdersPage.js:1196)
- Havia um comentário TODO `{/* ↓↓↓ COLE AQUI o bloco <TabsContent value="overdue"> ↓↓↓ */}` no lugar do TabsContent — nunca foi implementado.
- Backend `/api/service-orders/overdue-at` já retornava 93 OSs (validado com curl). Só faltava o container do lado do React.
- Fix: implementado TabsContent com cards (visual vermelho), filtros por status (Aguardando Análise A.T / Peças / Conserto), busca, badge de dias, link WhatsApp e navegação clicando no card (`handleOrderClick` — mesmo fluxo do Histórico).

### 7. Campainha tocando ao mudar de página (DashboardLayout.js:200)
- DashboardLayout é usado por cada página individual → desmonta a cada rota → `seenAlertIdsRef` (useRef) resetava a Set vazia → primeiro `poll()` interpretava TODOS os alertas como "novos" → `audioRef.current.play()`.
- Fix: adicionado `alertsFirstPollRef` que sinaliza o primeiro poll após montar. O áudio só toca se houver item novo E não for o primeiro poll. Os IDs continuam sendo populados no ref.
- Pattern espelha o segundo useEffect (linha 227) que já usava `lastExtCountRef.current !== null` pra mesma proteção.

### 8. Adesivo personalizado imprimindo torto / vários por impressão (LabelTemplatesPage.js + printingService.js)
- CSS antigo: `@page { size: 50mm 30mm; margin: 0 }` sem `landscape`, sem `page-break-after`, sem margem para o liner de 4mm da bobina 58mm.
- Consequência: impressora térmica alinhava conteúdo em pé, fora da margem, e cuspia várias etiquetas em branco antes de sair uma correta.
- Fix: criada função `printCustomLabel(pngDataUrl, { sizeKey, customContent, name })` em `printingService.js` que replica EXATAMENTE a geometria de `printOSLabel`/`printProductLabel`:
  * paper = 58×30mm (com 4mm de liner) para preset `50×30`
  * `landscape` explícito
  * `page-break-after: always` + `break-inside: avoid`
  * screen preview 3× antes de imprimir + botão explícito (não auto-print)
- `LabelTemplatesPage.print()` agora mapeia size preset → sizeKey e delega para `printCustomLabel`. Presets 80×50 e 100×50 sem liner (paper = content). Tamanhos custom = paper próprio.

## Sessão 30/08/2026 (parte 2) — Link de assinatura remota via WhatsApp

### 9. Link de assinatura pelo celular do cliente
Cenário: o técnico está no cliente, mas o cliente não está presente (ou o técnico terminou o serviço e voltou para a loja). Antes só havia opção do cliente assinar no aparelho do técnico. Agora é possível gerar um link único que o cliente abre no próprio celular e assina.

**Backend (`server.py`)**:
- Nova collection MongoDB `signature_links` (sidecar): `{token, os_number, technician_signature, technician_name, client_name_hint, client_cpf_hint, status, created_at, expires_at, used_at}`.
- `POST /api/service-orders/{os}/signature-link` (auth): gera `uuid4` como token, salva a assinatura do técnico + metadados, monta URL absoluta usando o `Origin`/`Referer` da chamada, monta mensagem WhatsApp pronta com `wa.me/55{phone}?text=...`. TTL 7 dias.
- `GET /api/public/sign/{token}` (público): retorna só dados essenciais da OS (número, cliente, produto, defeito, técnico, status) — SEM telefone/endereço/valores. Valida expiração, status `used` e se a OS já foi assinada por outro caminho.
- `POST /api/public/sign/{token}/submit` (público): aceita `signature_client` + `client_cpf` opcional. Persiste na OS reusando o mesmo pipeline de `sign_service_order` (Assinafy PDF em background). Marca token como `used` — single-use.

**Frontend**:
- Nova rota pública `/sign/:token` em `App.js` renderiza `PublicSignPage.js`. Visual clean, mobile-first: 
  - Header com badge "Link seguro" (verde)
  - Card "Confira os dados" com dados da OS em grid 2 colunas
  - Card "Sua assinatura" com canvas retina-aware (DPR)+ campo CPF opcional
  - Botão "Confirmar Assinatura" dark (slate-900) — grande, tap-friendly
  - Estados: loading (spinner), erro (link expirado/usado), sucesso (ícone de escudo verde + "Assinatura registrada")
- `SignatureModal.js`: no Step 3, além do canvas de assinatura, agora há um card `"Cliente não está presente? [Enviar link]"` (accent verde). Ao clicar:
  1. Chama o endpoint de criação
  2. Reconstrói a URL sempre com `window.location.origin` (evita cluster-hostname interno)
  3. Substitui a URL na mensagem do wa.me
  4. Abre `wa.me` em nova aba
  5. Mostra card verde "Link enviado" com URL + botão "Copiar" + botão "Fechar (aguardando cliente assinar)"

## Sessão 15/09/2026 — Fix completo dos scrapers Hisense e HQ

### 13. Scraper capturando dados desalinhados (Hisense + HQ) — CRÍTICO
**Sintoma**: usuário reportou que scraper Hisense estava salvando OSs com todos os campos deslocados: nome=telefone, produto=modelo, modelo="MG", tipo_atendimento="3", defeito=service_type. HQ com sintoma similar (nome="BELO HORIZONTE").

**Root causes identificadas** (múltiplas, em série):
1. **`run_sync_manual.py` conectava ao MongoDB via Motor**, mas o app real usa Supabase. Scraper "capturava" OSs no MongoDB local que ninguém lê. Fix: importar `db` do `supabase_db` no script manual.
2. **Guard de colisão sempre skipava OSs criadas manualmente** (source=`local`). Fix: auto-migrate para `telecontrol_*` quando fonte antiga é local/mastermaq (caso ARTHUR).
3. **`fetch_order_details` retornando None era silenciosamente ignorado** com `if details:`. Fix: log error + adicionar ao result.errors.
4. **Índices fixos `cells[X]`** quebravam a cada mudança de layout do Telecontrol. Fix estrutural: mapeamento header-based lendo `<thead th>` em runtime, normalização (lowercase + strip acentos), fallback para índice legado.
5. **Telecontrol tem `<th>` "sorting_asc"** vazio extra no início do thead que o tbody não replica → todos os campos ficaram +1 deslocados. Fix: `cellOffset = 1` fixo.
6. **HQ tem layout de tabela completamente diferente** do Hisense (14 headers vs 28, ordem diferente). Fix: dropar TODOS os campos do summary da HQ + forçar `fetch_order_details` quando `customer_name` existente parece cidade ou dígitos.
7. **Cor "Tomada"** (`rgb(143, 188, 143)`) não mapeada. Adicionada ao `statusColorMap`.

**Instrumentação nova**:
- `diagnostic.total_rows / skipped_few_cells / skipped_no_os_number / parse_errors` — expõe drops silenciosos na extração JS
- `diagnostic.headers / header_map / thead_raw / first_row_dump` — permite ver exatamente o que o Telecontrol está entregando
- Log `Fetched details for OS X: NAME` para cada detail page bem-sucedida
- Log `MIGRANDO` para OSs auto-migradas de local → telecontrol_*
- Log `INSERIDA` para cada nova OS persistida
- Log `Volume anômalo` com histórico dos últimos ciclos

**Resultados finais**:
- Hisense: 61 OSs extraídas, 5 novas inseridas (ELAINE, ANDRE, BERTONY, JANATAS, ELOISA), ARTHUR migrado, 57 atualizadas com nome/produto/modelo/tipo/defeito corretos.
- HQ: 2 novas + 16 atualizadas via detail page. Nomes reais restaurados (VICTOR, PATRICIMARA, RENATO, BRUNA, etc.).

**Arquivos modificados**:
- `/app/backend/telecontrol_scraper.py` — refatoração da extração JS + collision guard + HQ layout fix + logs
- `/app/backend/run_sync_manual.py` — trocar Mongo por Supabase + sync_logs opcional
- `/app/backend/tests/dump_missing_os.py`, `test_find_one_missing.py` — scripts de diagnóstico



## Sessão 31/08/2026 — Fixes: link duplicado + fluxo cliente-primeiro

### 11. Bug: mensagem WhatsApp com URL duplicada (`https://.../https://.../sign/...`)
- **Causa**: no `SignatureModal.js`, o `handleSendLink` fazia 2 regex sucessivos sobre a mensagem retornada pelo backend. O 1º substituía uma URL absoluta correta pela mesma URL absoluta. O 2º substituía o path `/sign/<token>` (que ainda existia no resultado) pela URL ABSOLUTA — criando concatenação `https://mastermaq-system.onlinehttps://mastermaq-system.online/sign/...`.
- **Fix**: reconstruir a mensagem inteira do zero no frontend usando `window.location.origin + token + order.customer_name + order.product + order.phone1`. Backend continua devolvendo `url` e `whatsapp_url`, mas o frontend agora IGNORA e monta do zero — comportamento 100% previsível.

### 12. Feature: fluxo "cliente assina primeiro, técnico completa depois"
Antes: `technician_signature` era OBRIGATÓRIO no `POST /signature-link` — o técnico precisava assinar ANTES de enviar o link. Depois do fix:

**Backend (`server.py`)**:
- `SignatureLinkCreate.technician_signature: Optional[str]` — aceita `null`.
- `POST /public/sign/{token}/submit`: quando o link NÃO tinha `technician_signature`, persiste SOMENTE `signature_client` + CPF na OS. Retorna `fully_signed: false`. Assinafy NÃO é disparado.
- `POST /service-orders/{os}/sign`: `signature_technician` e `signature_client` viraram opcionais. Só bloqueia (400) se as duas JÁ existem. Faz update parcial — pode receber só a parte do técnico e mesclar com o cliente já salvo. Assinafy dispara automaticamente quando as duas ficam presentes.
- `GET /service-orders/{os}/signatures` agora retorna também `signature_client_name`, `signature_client_cpf`, `signature_tech_name`.

**Frontend (`SignatureModal.js`)**:
- Novo `useEffect` no `open` que faz `GET /signatures` e detecta o estado parcial (`existingClientSig` / `existingTechSig`).
- Novo modo **"completion"** — quando a OS tem só `signature_client`, o modal renderiza uma UI compacta:
  * Header: "Completar Assinatura — OS #####"
  * Card verde "Cliente já assinou" com **CPF exibido** e preview da assinatura
  * Input "Técnico *" (nome)
  * Canvas OU pill "Assinatura salva encontrada" (se `localStorage` tem sig do técnico) + "Refazer"
  * Botão "Confirmar" que chama `/sign` com só a parte do técnico → OS fica totalmente assinada
- Novo botão **"Enviar link para o cliente"** no Step 1 — permite enviar sem que o técnico assine antes (fluxo cliente-primeiro). Habilitado só quando o nome do cliente está preenchido.
- Preserva fluxo tradicional: se o técnico assina primeiro em Step 2 e envia o link em Step 3, o link carrega a assinatura do técnico e o submit do cliente já finaliza a OS.

**Testado end-to-end**:
- Link SEM tech sig → cliente submit → `fully_signed=false` → só client no /signatures
- Reabrir modal → completion mode com CPF e preview corretos
- `/sign` com só tech → OS completa (ambas assinaturas presentes) → 400 no re-submit
- Assinafy dispara só quando ambas ficam presentes
- **Sintoma**: após deploy, `POST /api/auth/login` em `mastermaq-system.online` retornava HTTP 520 imediato. Usuários não conseguiam logar.
- **RCA (deployer agent)**: backend saudável e ready no cluster, ZERO POST de login chegava ao uvicorn. Causa: loop de auto-sync Hisense lançava Playwright/chromium a cada 30 min → OOM-kill sob o tier_0 de 512Mi → conexões TCP recusadas/resetadas → Cloudflare devolvia 520 antes do request chegar no origin. `consecutive_failures: 367` no scraper Hisense com erros `spawn ETXTBSY` e `Executable doesn't exist`.
- **Fix aplicado em `server.py`**:
  * `startup_auto_sync()` agora respeita ENV `HISENSE_AUTO_SYNC_ENABLED` (default: `false`). Loop e watchdog só sobem se `=true`.
  * Quando desabilitado, o status Hisense é resetado para `"manual"` (novo estado — não dispara `down`/`warning` no `/api/scrapers/health`) e `consecutive_failures=0`. Badge do dashboard fica limpo.
  * `_load_health_from_db()` agora roda `await` (não `create_task`) ANTES do reset, para não sobrescrever depois.
  * Botão "Sincronizar" no painel continua funcionando (dispara `POST /api/telecontrol/sync` isolado, sem loop).
- **Testado local**: login `HTTP 200 in 0.459s`, health `overall: ok`, Hisense `status: manual`, HQ continua rodando normal.
- **Ação pendente do usuário**: redeploy para propagar o fix a produção. Após redeploy, se ainda quiser rodar auto-sync em preview, definir `HISENSE_AUTO_SYNC_ENABLED=true` em `backend/.env`.

## Stack
- Frontend: React 19 (CRA + Craco), Tailwind, Shadcn/UI, lucide-react, axios, react-router 6
- Backend: Python 3.11 + FastAPI + uvicorn (Supervisor porta 8001)
- DB primário: Supabase (PostgreSQL via PostgREST)
- DB secundário: MongoDB local
- Scraping: Playwright + Chromium
- Auth: JWT customizado (roles: admin, technician, invisacook)

## Ambientes
- Preview (dev): `https://2c89069e-d05b-494c-a8d1-ed71aa3f7761.preview.emergentagent.com`
- Produção: `https://mastermaq-system.online` (deploy manual pelo user quando OK)

## Sessão 30/09/2026 — Roteiro inteligente com IA + Mapa 3D

### 14. Sugestões de rota enriquecidas por LLM (Emergent LLM Key / OpenAI)
- **Backend** (`routes_module.py`): novo endpoint `POST /api/routes/analyze-suggestions` (autenticado).
  Recebe os 4 grupos pré-computados no frontend (Mais Próximas, Região Concentrada, Região Alternativa,
  Prioridade) e chama `gpt-5.4-mini` via `emergentintegrations` para retornar, para cada grupo:
  `rationale` (1-2 frases em pt-BR), `priority_score` (0-100), `tags` (perto-da-base, prioridade,
  atraso-alto, regiao-densa, alternativa) e `top_reason`.
  Considera: Região, Proximidade da Base, Tempo em aberto (>10 dias) e OSs marcadas como prioridade.
  Fallback determinístico se a LLM falhar/estiver indisponível — a UX nunca quebra.
  A chave `EMERGENT_LLM_KEY` NUNCA é exposta ao frontend.
- **Frontend** (`RoutesPage.js`): após `computeProximitySuggestions()` calcular os 4 grupos locais,
  dispara `POST /api/routes/analyze-suggestions` em paralelo (não bloqueia). O painel de sugestões
  agora exibe: badge de score IA (verde/amarelo/vermelho por urgência), rationale em texto pequeno,
  tags coloridas e indicador "analisando com IA…" enquanto carrega.

### 15. Filtros de Roteiro consolidados
- Paginação client-side (10/pág real) já entregue na sessão anterior — validada.
- Filtros de cidade/bairro/status agora agem sobre TODA a lista (limit=5000, page=1) ao invés das
  10 OSs da página atual. Filtros de bairro reduzem automaticamente ao selecionar cidades.
- Sugestões restritas aos status roteirizáveis (Aguardando Análise A.T, Conserto, Peças, Auditoria,
  Aberta Call-Center). MAX_OS por opção sobe de 8 → 20.
- Bloqueio de 8 fotos aplicado apenas para OS de `Garantia` (Orçamento libera direto).

### 16. Mapa estilo Google Maps 3D
- `RouteMapDialog.GoogleMap` agora usa `mapId: 'DEMO_MAP_ID'` (vector map),
  `tilt: 45` inicial e `rotateControl: true`.
- Em `handleMapLoad`: instancia `google.maps.TrafficLayer()` sobre o mapa (linhas verde/amarelo/
  vermelho de trânsito em tempo real, iguais ao Google Maps oficial). Guarda ref em
  `map.__trafficLayer` para não duplicar.
- Durante navegação (`watchPosition`): quando `speed > 3 km/h`, chama `map.setHeading(heading)` para
  rotacionar o mapa no sentido do movimento. `setTilt(60)` em follow-mode para dar profundidade 3D.
- `recenterOnTech`: zoom 18, tilt 60 ao retornar ao modo follow.
- `dragstart` manual: reseta heading=0 e tilt=45 para conforto de leitura.

### 17. "Compartilhar Localização" liberado a qualquer momento
- Botão no sidebar de cada parada agora aparece SEMPRE (antes só em pending/arrived/in_transit).
  Admin/técnico pode gerar o link do cliente antes mesmo de iniciar a navegação — o token
  público (`/tracking/share-token`) já é válido a partir da criação do roteiro.

**Arquivos modificados**:
- `/app/backend/routes_module.py` — novo endpoint `/analyze-suggestions` + models
- `/app/frontend/src/pages/RoutesPage.js` — chamada LLM + UI enriquecida + mapa 3D
  (tilt/heading/TrafficLayer/DEMO_MAP_ID) + libera compartilhar sempre

## Backlog restante
- P2: Migrar de `DEMO_MAP_ID` para um Map ID próprio do Google Cloud (permite estilos custom).
- P2: Sistema de alerta externo (SMS/Webhook) para falha crítica dos scrapers.
- P3: Migrar `image_url` / `product_type` do sidecar MongoDB para colunas nativas no Supabase.


## Sessão 30/09/2026 (parte 2) — Roteiro refinado + Mapa "arrow behind" + Status clean

### 18. Roteirização com 4 novos grupos (Região / Próximas / Tempo / Prioridade)
- **Grupos redesenhados** (RoutesPage.js `computeProximitySuggestions`):
  - **Região (Cluster Denso)**: encontra o cluster mais denso — para cada OS
    conta quantas outras estão em raio de 3 km; o cluster com maior contagem
    vira o grupo. Não é distância da base; é OSs perto UMA DAS OUTRAS.
  - **Próximas da Base**: todas as OSs até 15 km da base (Rua Descalvado 636,
    Renascença/BH — coord: -19.8881334, -43.9420748), ordenadas por distância.
    Sem cap artificial.
  - **Tempo**: OSs com >10 dias em aberto, ordenadas por dias_open desc.
  - **Prioridade**: apenas OSs com flag `priority=true`.
- **Multi-seleção**: cada card tem checkbox; botão "Aplicar (N)" une as OSs de
  todas as sugestões marcadas (dedupe). Clicar no card sem marcar aplica só
  aquele grupo.
- **Egress**: chamada LLM agora envia no máx. 25 OSs por grupo (cap por egress).

### 19. Fix `limit=5000` no fetch de OSs para roteirização
- **Backend** (`server.py`): o clamp anterior `limit = min(max(limit,1), 30)`
  cortava o retorno em 30 OSs mesmo quando o frontend pedia 5000. Agora, quando
  `exclude_status` está presente (é o modal de Criar Roteiro), o cap sobe para
  5000. O "X OS encontradas" agora reflete o total real filtrado (antes ficava
  fixo em ≤200).
- **Frontend**: `osTotalItems` e `osTotalPages` passam a ser recalculados no
  useEffect dos filtros — reflete o count após aplicar cidade/bairro/status.

### 20. Mapa "câmera atrás do técnico" (Google Maps style)
- **Ícone da seta**: nova `buildNavArrowSVG(heading, techName)` renderiza a
  seta azul de navegação (chevron com halo azul) igual ao Google Maps mobile.
  Substitui a moto no marcador do próprio técnico durante navegação.
- **Precisão de GPS**: `watchPosition` reduzido `timeout: 10000 → 5000`,
  `enableHighAccuracy: true` e `maximumAge: 0` já estavam.
- **Heading fallback (bússola)**: novo `useEffect` no `deviceorientation` /
  `deviceorientationabsolute`. Quando o GPS não devolve heading (celular
  parado / hardware sem suporte), lê o magnetômetro. iOS 13+ solicita permissão
  automaticamente via `DeviceOrientationEvent.requestPermission`.
  Guarda em `headingRef.current`.
- **recenterOnTech**: agora usa `map.setOptions({center, zoom:18, tilt:55,
  heading: headingRef.current})` — câmera aponta na direção do movimento
  ("por trás do técnico") como sugerido pelo usuário. Depois um `panBy(0,-80)`
  coloca a seta no terço inferior.
- **Auto-follow**: zoom 18 em vez de 17, tilt 60°, setHeading contínuo
  (sem gate de speed>3km/h — usa headingRef que já é filtrado).

### 21. StatusQuickAction — dropdown clean + fix 405
- **Design**: trocado `<select>` nativo por Shadcn `<Select>` — as OPÇÕES
  agora são branco/preto (classes `bg-white text-gray-900`) em vez de herdar
  a cor do status atual. O trigger continua colorido pelo status vigente
  (badge visual), mas o menu aberto é limpo/legível.
- **Fix 405** (`Erro ao mudar status: Method Not Allowed`):
  - Guarda `if (!order?.os_number)` no `patch()` — antes, quando o
    `os_number` estava undefined a URL virava `/api/service-orders/` e o
    servidor devolvia 405.
  - Payload PUT agora envia APENAS `{ status }` em vez de `{ ...order, status }` —
    evita conflitos com campos stale (fotos antigas, endereço em edição).
  - Guarda equivalente no autosave do OSDetailModal (linha ~2046).

**Arquivos modificados nesta parte 2**:
- `/app/backend/server.py` — clamp de limit adaptativo para `exclude_status`.
- `/app/frontend/src/pages/RoutesPage.js` — novos grupos, multi-seleção,
  seta de navegação SVG, deviceorientation, recenterOnTech redesenhado.
- `/app/frontend/src/pages/ServiceOrdersPage.js` — StatusQuickAction com
  Shadcn Select, guardas de os_number, payload mínimo no PUT.


### 22. Fix 405 nas OSs do Telecontrol com `#` no os_number — RCA
- **Causa raiz**: OSs importadas via scraper HQ/Hisense têm `os_number` no
  formato `'#71693600 '` (prefixo `#` + espaço final). Dois pontos de falha:
  1. **Frontend**: ao montar a URL `${API}/service-orders/${order.os_number}`,
     o `#` virava separador de fragmento. O browser truncava a URL em
     `/api/service-orders/` → servidor devolvia **405 Method Not Allowed**
     (não existe PUT em `/service-orders/`).
  2. **Backend (`supabase_db.py`)**: mesmo quando a URL chegava correta
     (`%23`), o filtro gerado para o Supabase (`os_number=eq.#71693600 `) ia
     RAW na querystring. O `#` quebrava a URL do próprio PostgREST → filtro
     chegava vazio → 404 "Ordem não encontrada".
- **Fix frontend**: todas as 21 chamadas Axios que usam `${order.os_number}`
  (ou similar) na URL agora envolvem o valor em `encodeURIComponent(...)`.
  Arquivos afetados: `ServiceOrdersPage.js` (15), `LaudoModal.js` (3),
  `OrderDetailOverlay.js` (2), `RoutesPage.js` (1).
- **Fix backend** (`supabase_db.py`): novo helper `_pgrst_encode(v)` que
  aplica `urllib.parse.quote(v, safe='')` em TODOS os valores que vão para
  querystring PostgREST (`=eq.`, `=ilike.`, `=in.`, `=nin.`, `=ne.`, `=gte.`,
  `=lte.` e também dentro de `$or`).
- **Validado via curl**:
  - PUT `/api/service-orders/%2371693600%20` body `{status:"Aguardando Peças"}` → **HTTP 200**
    (resposta: `os_number='#71693600 '`, `status='Aguardando Peças'`).
  - PUT em OS normal (27888) → **HTTP 200** (sem regressão).
  - GET listagem → total 7054, overdue 27.

**Arquivos modificados**:
- `/app/backend/supabase_db.py` — helper `_pgrst_encode` + encode em
  todos os filtros gerados.
- `/app/frontend/src/pages/ServiceOrdersPage.js`
- `/app/frontend/src/pages/RoutesPage.js`
- `/app/frontend/src/components/LaudoModal.js`
- `/app/frontend/src/components/OrderDetailOverlay.js`


## Sessão 05/10/2026 — Fase 1 do refactor de Tracking/Navegação

### 23. `distanceToPath` com projeção perpendicular ao segmento
- **Antes**: calculava só distância aos VÉRTICES da polyline → carro a 10m da
  reta A-B (mas 100m de A e 100m de B) era avaliado como 100m fora da rota.
  Isso atrasava o off-route detection ou disparava recálculos tardios.
- **Agora** (`RoutesPage.js`): projeção equiretangular (válida p/ <10km, erro
  <0.5%) + projeção escalar `t ∈ [0,1]` em cada segmento + clamp aos endpoints
  quando o ponto está fora do intervalo. Validado numericamente:
  - Perpendicular 10m real → algoritmo retorna 10.0m (antes: 105.0m)
  - Além do vértice A → retorna 104.6m (até A, correto)
  - Sobre a linha → retorna 0.00m

### 24. Filtros de precisão GPS (accuracy + salto impossível)
- **Filtro 1 — accuracy > 60m**: Celulares em prédios devolvem fixes de
  150-500m. Antes isso ia direto para câmera/off-route detection. Agora
  rejeitamos (exceto o primeiro fix, que é necessário para iniciar o
  tracking).
- **Filtro 2 — salto impossível**: Se dMeters > 200m entre dois fixes
  consecutivos E velocidade instantânea > 180 km/h → descarta. Novo
  `lastFixTsRef` guarda timestamp do último fix aceito.

### 25. ETA e cor de trânsito corretos no backend
- **Antes**: `nav_duration_seconds` e `nav_duration_in_traffic_seconds`
  recebiam o MESMO valor → admin perdia a distinção entre tempo planejado e
  tempo real com trânsito. `nav_traffic_color: 'segmented'` não existia no
  colorMap do admin → caía no azul padrão silenciosamente.
- **Agora**:
  - `nav_duration_seconds` ← `duration_seconds` (planejado).
  - `nav_duration_in_traffic_seconds` ← `duration_in_traffic_seconds`
    (com trânsito, fallback para o planejado).
  - UI mostra o tempo COM trânsito, não o idealizado.
  - Nova função `aggTrafficColor()` calcula a cor agregada da rota a partir
    dos `speedReadingIntervals`, retornando `green` / `yellow` / `red`
    (compatível com o colorMap do admin). >25% em `TRAFFIC_JAM` → red;
    >35% em `JAM+SLOW` → yellow; resto → green.

### 26. Fallback "Calculando rota..." em vez de linha reta enganosa
- **Antes**: enquanto a API `/nav-leg` respondia, desenhávamos uma linha
  reta Técnico→OS. Dava impressão de "atravessa prédios/quarteirões".
- **Agora**: se já há rota real desenhada, MANTEMOS ela durante o
  recálculo (sem flicker). Se é primeira chamada, mostramos o texto
  "Calculando rota..." no painel de próxima instrução. Erro de API → texto
  "Rota indisponível - verifique conexão", rota antiga continua visível.

### 27. JWT_SECRET fail-fast (segurança)
- **Antes**: `JWT_SECRET = os.environ.get('JWT_SECRET', 'default_secret')`
  — se a env var sumisse, o backend subia usando `default_secret`, abrindo
  caminho para forja de tokens.
- **Agora** (`server.py`, `tracking_module.py`, `routes_module.py`):
  importação levanta `RuntimeError` se `JWT_SECRET` não existir OU for
  um dos valores inseguros (`default_secret`, `change-me`, vazio). Backend
  não sobe — falha explícita no startup. Validado: remover a env var =
  `RuntimeError: JWT_SECRET ausente ou inseguro em backend/.env`.

**Arquivos modificados nesta Fase 1**:
- `/app/frontend/src/pages/RoutesPage.js` — distanceToPath perpendicular,
  filtros GPS (accuracy + jump), ETA/cor de trânsito corretos, fallback
  "Calculando rota".
- `/app/backend/server.py` — JWT_SECRET fail-fast.
- `/app/backend/tracking_module.py` — JWT_SECRET fail-fast.
- `/app/backend/routes_module.py` — JWT_SECRET fail-fast.



## Sessão 20/10/2026 — Migração p/ novo ambiente + bugs + Tracking Fase 2
Repo `vrf165309-alt/systemmaq` clonado em /app; `backend/.env` restaurado com as chaves do usuário. Regra do usuário: seguir Ponytail (código mínimo), NÃO usar testing agent/outros agentes.

### 28. Scraper Hisense desalinhado (telecontrol_scraper.py)
- Diagnóstico ao vivo: thead=30 e tbody=30 (1:1). `headerIndex` já soma `headerOffset`, mas `cellOffset=1` somava +1 de novo → nome=CPF, telefone=nome, tipo=defeito, série=abertura, modelo=descrição.
- Fix: `cellOffset = 0`. Validado na lista real (tipo "Garantia com deslocamento", modelo = referência, telefone capturado).
- Detail page Hisense: "Nome" casa com "Nome Comercial" do produto → OS nova agora prefere customer_name/model/serial da lista.
- OS existentes: lista corrige os campos no próximo sync; phone1 sem dígitos (nome gravado pelo bug) é limpo.

### 29. Botão Sincronizar → 2 subprocessos simultâneos
- `run_background_sync` roda `run_sync_manual.py --start <hoje-1 mês> --end <hoje> --source hisense` e `--source hq` em paralelo (asyncio subprocess). Contadores lidos do log "Concluído: X novas, Y atualizadas". Seletor 60/90/180/365 dias continua usando dias.

### 30. Enviar Cópia — PDF/link permanente
- `/api/files/temp-pdf` salva no object storage (`mastermaq-manuais/shared-pdfs/{token}.pdf`), sem expiração e sobrevive a restart (antes: memória + 24h).

### 31. Manuais 500
- Os 56 manuais baixam OK no preview. `get_object` agora renova `storage_key` em 401/403 e tenta 1x; log inclui path. Se persistir em produção: conferir secret `EMERGENT_LLM_KEY` de produção.

### 32. Tracking Fase 2 + polling de trânsito (RoutesPage.js)
- `snapToPath` (marker/câmera grudam na rota se <30m); `distanceToPath` reusa.
- Heading filtrado (`smoothHeading` low-pass circular); bússola só após 3s sem heading do GPS.
- Câmera com estado próprio (`cameraStateRef` + rAF `moveCamera`, para ao convergir); centro 65m à frente no sentido do heading.
- Bug corrigido: `prevPosRef` era recriado a cada fix, zerando `_offRouteStreak/_lastNavUpdate/_lastBreadcrumb` → off-route nunca recalculava e breadcrumb/gps ia a cada fix. Agora preservados (breadcrumb/gps a cada 10s como projetado).
- Polling `/nav-leg` a cada 20s: se geometria nova a <25m da atual, troca só segmentos coloridos + ETA; senão redesenha.

### 33. Fase 3 — Recálculo + Realtime + TTL (20/10/2026)
- Recálculo inteligente: limiar off-route adaptativo pela precisão do GPS (50–120m), detecção de contramão (heading >135° oposto ao trecho a >15km/h), 3 leituras seguidas, mínimo 8s entre recálculos.
- Realtime: `frontend/.env` não tinha `REACT_APP_SUPABASE_URL/ANON_KEY` → `supabase` era null (canal nunca existiu). Adicionados. Técnico faz broadcast em `tracking-{routeId}`: `gps` (cada fix, posição snapped), `nav` (rota+trânsito), `statuses`, `end`. Admin escuta o canal; polling caiu de 5s → 30s (fallback/late joiners). Broadcast validado no navegador (anon key).
- TTL: `tracking_breadcrumbs.created_at` (Date) + índice TTL 30 dias criado no startup. Docs antigos sem created_at não expiram.

### 34. Fase 4 — Instruções + Map ID
- Voz em camadas: "Em 800/500/200 metros, …" e instrução a <50m; cada aviso falado 1x por step; pula steps ultrapassados. Bug corrigido: chegada em parada sobrescrevia `lastSpokenRef` (reiniciava os steps) → agora `lastArrivalRef`.
- Map ID: `REACT_APP_GOOGLE_MAP_ID` (fallback `DEMO_MAP_ID`). Usuário precisa criar Map ID vetorial no Google Cloud e informar.

### Próximo
- Informar Map ID próprio; validar navegação em campo.
