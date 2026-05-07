#!/usr/bin/env python3
"""ADW: WhatsApp Monthly Check-in — disparo mensal de relacionamento com clientes via Evo Go"""

import json
import logging
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DOTENV_PATH = WORKSPACE_ROOT / ".env"
CONTACTS_FILE = WORKSPACE_ROOT / "workspace" / "data" / "contacts_whatsapp.json"
LOG_FILE = WORKSPACE_ROOT / "workspace" / "data" / "whatsapp_sends_log.json"

# ── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ── Config ────────────────────────────────────────────────────────────
def load_dotenv():
    """Carrega variáveis do .env sem sobrescrever as já definidas."""
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


def get_evogo_config():
    url = os.environ.get("EVOLUTION_GO_URL", "").rstrip("/")
    # Para envio usa o token da instância; fallback para a chave global
    key = os.environ.get("EVOLUTION_GO_INSTANCE_TOKEN") or os.environ.get("EVOLUTION_GO_KEY", "")
    if not url:
        raise ValueError("EVOLUTION_GO_URL não configurada no .env")
    if not key:
        raise ValueError("EVOLUTION_GO_INSTANCE_TOKEN (ou EVOLUTION_GO_KEY) não configurada no .env")
    return url, key


def get_crm_config():
    url = os.environ.get("EVO_CRM_URL", "").rstrip("/")
    token = os.environ.get("EVO_CRM_TOKEN", "")
    pipeline_id = "1fd69461-165f-4f9b-b36b-3181a0e5be89"
    return url, token, pipeline_id


# ── CRM Integration (com fallback para JSON local) ────────────────────
def fetch_contacts_from_crm(crm_url, crm_token, pipeline_id):
    """Busca itens do pipeline no CRM. Retorna lista de contatos ou None."""
    try:
        url = f"{crm_url}/api/v1/pipelines/{pipeline_id}/pipeline_items"
        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "api_access_token": crm_token,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
            if not data.get("success"):
                log.warning(f"CRM retornou erro: {data}")
                return None
            items = data.get("data", [])
            if not items:
                log.info("CRM pipeline vazio — usando fallback JSON local")
                return None
            # Extrai nome + telefone de cada item do pipeline
            contacts = []
            for item in items:
                contact = item.get("contact") or item.get("conversation", {}).get("meta", {}).get("sender", {})
                name = contact.get("name") or item.get("name", "Cliente")
                phone = contact.get("phone_number") or contact.get("phone", "")
                if phone:
                    phone = str(phone).strip().lstrip("+")
                stage = item.get("stage", {}).get("name", "")
                contacts.append({"name": name, "phone": phone, "stage": stage})
            log.info(f"CRM pipeline: {len(contacts)} itens carregados")
            return contacts
    except Exception as e:
        log.warning(f"CRM não disponível ({e}), usando fallback JSON local")
        return None


def load_contacts_local():
    """Carrega contatos do arquivo JSON local."""
    if not CONTACTS_FILE.exists():
        log.error(f"Arquivo de contatos não encontrado: {CONTACTS_FILE}")
        return []
    with open(CONTACTS_FILE) as f:
        data = json.load(f)
    contacts = data.get("contacts", [])
    # Filtra apenas ativos e com stage != inativo
    active = [
        c for c in contacts
        if c.get("active", False) and c.get("stage", "").lower() != "inativo"
    ]
    log.info(f"Contatos locais carregados: {len(contacts)} total, {len(active)} ativos")
    return active


def load_contacts(crm_url, crm_token, pipeline_id):
    """Carrega contatos: tenta CRM primeiro, fallback para JSON local."""
    crm_contacts = fetch_contacts_from_crm(crm_url, crm_token, pipeline_id)
    if crm_contacts is not None:
        return crm_contacts, "crm"
    return load_contacts_local(), "local"


# ── WhatsApp Send ─────────────────────────────────────────────────────
def build_message(name):
    """Monta a mensagem personalizada de check-in."""
    first_name = name.split()[0] if name else "Cliente"
    return (
        f"Olá {first_name}! 👋 Tudo bem?\n\n"
        "Passando pra saber se você precisa de algo da nossa parte. "
        "Estamos sempre à disposição! 😊"
    )


def send_whatsapp(evogo_url, evogo_key, phone, message):
    """Envia mensagem de texto via Evolution Go."""
    # Normaliza para JID se necessário
    number = phone if "@" in str(phone) else f"{phone}@s.whatsapp.net"
    payload = json.dumps({"number": number, "text": message}).encode("utf-8")
    req = urllib.request.Request(
        f"{evogo_url}/send/text",
        data=payload,
        method="POST",
        headers={
            "apikey": evogo_key,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return {"success": True, "response": result}
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read())
        except Exception:
            error_body = str(e)
        return {"success": False, "error": f"HTTP {e.code}", "details": error_body}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Log ───────────────────────────────────────────────────────────────
def load_log():
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def save_log(entries):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False, default=str)


# ── Main ──────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("📲  WhatsApp Monthly Check-in")
    print(f"    Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    load_dotenv()

    # Configurações
    try:
        evogo_url, evogo_key = get_evogo_config()
    except ValueError as e:
        log.error(str(e))
        sys.exit(1)

    crm_url, crm_token, pipeline_id = get_crm_config()

    # Carrega contatos
    contacts, source = load_contacts(crm_url, crm_token, pipeline_id)
    print(f"\n📋 Contatos carregados ({source}): {len(contacts)}")

    if not contacts:
        print("⚠  Nenhum contato ativo encontrado. Abortando.")
        sys.exit(0)

    # Histórico de envios do mês atual
    run_log = load_log()
    this_month = datetime.now().strftime("%Y-%m")
    already_sent = {
        entry["phone"]
        for entry in run_log
        if entry.get("month") == this_month and entry.get("success")
    }

    sent_ok = 0
    sent_skip = 0
    sent_fail = 0
    run_entries = []

    for contact in contacts:
        name = contact.get("name", "Cliente")
        phone = str(contact.get("phone", "")).strip()

        if not phone:
            log.warning(f"Contato '{name}' sem telefone — pulando")
            sent_skip += 1
            continue

        if phone in already_sent:
            log.info(f"Já enviado este mês para {name} ({phone}) — pulando")
            sent_skip += 1
            continue

        message = build_message(name)
        print(f"\n→ Enviando para {name} ({phone})…", end=" ", flush=True)

        result = send_whatsapp(evogo_url, evogo_key, phone, message)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "month": this_month,
            "name": name,
            "phone": phone,
            "source": source,
            "success": result["success"],
        }
        if not result["success"]:
            entry["error"] = result.get("error")
            entry["details"] = result.get("details")

        run_entries.append(entry)

        if result["success"]:
            print("✅ OK")
            sent_ok += 1
        else:
            print(f"❌ FALHOU — {result.get('error')}")
            sent_fail += 1

        # Delay entre envios para não parecer spam
        if contact != contacts[-1]:
            time.sleep(2)

    # Salva log
    run_log.extend(run_entries)
    # Mantém apenas os últimos 6 meses
    cutoff = datetime.now().strftime("%Y-%m")
    run_log = [e for e in run_log if e.get("month", "") >= "2026-"]
    save_log(run_log)

    # Resumo
    print("\n" + "=" * 60)
    print(f"✅ Enviados com sucesso : {sent_ok}")
    print(f"⏭  Pulados (já enviados): {sent_skip}")
    print(f"❌ Falhas               : {sent_fail}")
    print(f"📄 Log salvo em        : {LOG_FILE}")
    print("=" * 60)

    if sent_fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠  Cancelado.")
        sys.exit(0)
