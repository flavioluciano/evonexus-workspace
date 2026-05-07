#!/usr/bin/env python3
"""
ADW: CRM Pipeline Sync — adiciona automaticamente novos contatos/conversas ao pipeline capitacao.

Fluxo:
  1. Busca todos os contatos do CRM
  2. Busca itens atuais do pipeline
  3. Identifica contatos sem item no pipeline
  4. Tenta criar pipeline item para cada novo contato
  5. Loga resultado (sucesso, falha, já existente)

Enquanto o bug da API pipeline_items estiver ativo, os itens vão para
a fila pendente em workspace/data/crm_pipeline_pending.json para adição
manual via UI em xfoodcrm.fhtech.app.br.
"""

import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DOTENV_PATH    = WORKSPACE_ROOT / "config" / ".env"
PENDING_FILE   = WORKSPACE_ROOT / "workspace" / "data" / "crm_pipeline_pending.json"
LOG_FILE       = WORKSPACE_ROOT / "workspace" / "data" / "crm_pipeline_sync_log.json"

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ── Config ─────────────────────────────────────────────────────────────────────
def load_dotenv():
    if not DOTENV_PATH.exists():
        return
    with open(DOTENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


PIPELINE_ID = "1fd69461-165f-4f9b-b36b-3181a0e5be89"
STAGE_ID    = "8d2165df-01a4-40a0-b9f2-6f2a27224ecb"  # "novo lead" — stage 1


def get_crm_config():
    url   = os.environ.get("EVO_CRM_URL", "").rstrip("/")
    token = os.environ.get("EVO_CRM_TOKEN", "")
    if not url:
        raise ValueError("EVO_CRM_URL não configurada no config/.env")
    if not token:
        raise ValueError("EVO_CRM_TOKEN não configurada no config/.env")
    return url, token


# ── CRM API helpers ─────────────────────────────────────────────────────────────
def crm_get(url, token, path, params=None):
    full_url = f"{url}/api/v1/{path}"
    if params:
        from urllib.parse import urlencode
        full_url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(
        full_url,
        headers={"api_access_token": token, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def crm_post(url, token, path, body):
    full_url = f"{url}/api/v1/{path}"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        full_url,
        data=data,
        method="POST",
        headers={
            "api_access_token": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()), None
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read())
        except Exception:
            error_body = str(e)
        return None, {"http_status": e.code, "body": error_body}


# ── Fetch contacts (paginado) ───────────────────────────────────────────────────
def fetch_all_contacts(crm_url, token):
    contacts = []
    page = 1
    while True:
        data = crm_get(crm_url, token, "contacts", {"page": page, "page_size": 100})
        batch = data.get("data", [])
        if isinstance(batch, dict):
            # alguns endpoints retornam {"data": {"payload": [...]}}
            batch = batch.get("payload", [])
        if not batch:
            break
        contacts.extend(batch)
        meta = data.get("meta", {})
        pagination = meta.get("pagination", {})
        if not pagination.get("has_next_page", False):
            break
        page += 1
        time.sleep(0.3)
    return contacts


# ── Fetch pipeline items (paginado) ─────────────────────────────────────────────
def fetch_pipeline_contact_ids(crm_url, token, pipeline_id):
    """Retorna set de contact_ids já presentes no pipeline."""
    contact_ids = set()
    page = 1
    while True:
        data = crm_get(crm_url, token, f"pipelines/{pipeline_id}/pipeline_items",
                       {"page": page, "page_size": 100})
        items = data.get("data", [])
        if not items:
            break
        for item in items:
            # tenta pegar contact_id de diferentes estruturas possíveis
            cid = (item.get("contact_id")
                   or item.get("contact", {}).get("id")
                   or item.get("conversation", {}).get("meta", {}).get("sender", {}).get("id"))
            if cid:
                contact_ids.add(str(cid))
        meta = data.get("meta", {})
        pagination = meta.get("pagination", {})
        if not pagination.get("has_next_page", False):
            break
        page += 1
        time.sleep(0.3)
    return contact_ids


# ── Pipeline item creation ───────────────────────────────────────────────────────
def try_add_to_pipeline(crm_url, token, contact_id, stage_id, pipeline_id):
    """
    Tenta criar pipeline item via API.
    Enquanto o bug pipeline_items POST estiver ativo, retorna (False, error_details).
    """
    resp, err = crm_post(crm_url, token, f"pipelines/{pipeline_id}/pipeline_items", {
        "contact_id": contact_id,
        "stage_id":   stage_id,
    })
    if err:
        return False, err
    if resp and resp.get("success"):
        return True, None
    return False, resp


# ── Pending queue ────────────────────────────────────────────────────────────────
def load_pending():
    if not PENDING_FILE.exists():
        return {}
    with open(PENDING_FILE) as f:
        return json.load(f)


def save_pending(pending):
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PENDING_FILE, "w") as f:
        json.dump(pending, f, indent=2, ensure_ascii=False, default=str)


# ── Run log ──────────────────────────────────────────────────────────────────────
def load_run_log():
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def save_run_log(entries):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(entries[-500:], f, indent=2, ensure_ascii=False, default=str)


# ── Main ─────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("🔄  CRM Pipeline Sync")
    print(f"    Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"    Pipeline: {PIPELINE_ID}")
    print(f"    Stage: novo lead ({STAGE_ID})")
    print("=" * 60)

    load_dotenv()

    try:
        crm_url, token = get_crm_config()
    except ValueError as e:
        log.error(str(e))
        sys.exit(1)

    # Buscar contatos e itens do pipeline
    print("\n📥 Buscando contatos do CRM...")
    contacts = fetch_all_contacts(crm_url, token)
    print(f"   → {len(contacts)} contato(s) encontrado(s)")

    print("📋 Verificando pipeline atual...")
    pipeline_contact_ids = fetch_pipeline_contact_ids(crm_url, token, PIPELINE_ID)
    print(f"   → {len(pipeline_contact_ids)} contato(s) já no pipeline")

    # Identificar novos (não estão no pipeline)
    new_contacts = [c for c in contacts if str(c.get("id", "")) not in pipeline_contact_ids]
    print(f"\n🆕 Novos contatos para adicionar: {len(new_contacts)}")

    if not new_contacts:
        print("\n✅ Nenhum contato novo. Pipeline sincronizado.")
        return

    # Carregar fila de pendentes
    pending = load_pending()
    run_log = load_run_log()

    added_ok  = 0
    added_fail = 0
    already_pending = 0
    run_entries = []

    for contact in new_contacts:
        cid   = str(contact.get("id", ""))
        name  = contact.get("name", "Sem nome")
        phone = contact.get("phone_number", "")

        print(f"\n→ {name} ({phone})...", end=" ", flush=True)

        # Tentar via API
        success, error = try_add_to_pipeline(crm_url, token, cid, STAGE_ID, PIPELINE_ID)

        entry = {
            "timestamp":   datetime.now().isoformat(),
            "contact_id":  cid,
            "name":        name,
            "phone":       phone,
            "pipeline_id": PIPELINE_ID,
            "stage_id":    STAGE_ID,
            "success":     success,
        }

        if success:
            print("✅ Adicionado ao pipeline")
            added_ok += 1
            # Remover da fila pendente se estava lá
            pending.pop(cid, None)
        else:
            print(f"⏳ API indisponível — adicionado à fila")
            added_fail += 1
            entry["error"] = str(error)
            # Adicionar à fila de pendentes se ainda não estiver
            if cid not in pending:
                pending[cid] = {
                    "name":       name,
                    "phone":      phone,
                    "added_at":   datetime.now().isoformat(),
                    "pipeline_id": PIPELINE_ID,
                    "stage_id":   STAGE_ID,
                    "crm_url":    f"{crm_url}/app/contacts/{cid}",
                }
                already_pending += 0
            else:
                already_pending += 1

        run_entries.append(entry)
        time.sleep(0.5)

    # Salvar estado
    save_pending(pending)
    run_log.extend(run_entries)
    save_run_log(run_log)

    # Resumo
    print("\n" + "=" * 60)
    print(f"✅ Adicionados via API : {added_ok}")
    print(f"⏳ Na fila (pendente)  : {added_fail}")
    print(f"📄 Log                : {LOG_FILE}")

    if pending:
        print(f"\n⚠️  {len(pending)} contato(s) aguardam adição manual:")
        print(f"   → Acesse: https://xfoodcrm.fhtech.app.br")
        print(f"   → Pipeline: capitacao → arraste para 'novo lead'")
        print(f"\n   Contatos pendentes:")
        for cid, info in list(pending.items())[:10]:
            print(f"   • {info['name']} ({info.get('phone', '')}) — {info['crm_url']}")
        if len(pending) > 10:
            print(f"   ... e mais {len(pending) - 10} (ver {PENDING_FILE})")

    print("=" * 60)

    # Exit 1 se há pendentes (permite ao scheduler/monitoramento detectar)
    if added_fail > 0 and added_ok == 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cancelado.")
        sys.exit(0)
