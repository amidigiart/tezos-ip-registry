"""
Generare SHA-256 hash-uri pentru înregistrare pe Tezos blockchain.
Titular: Mihai Roșca · QID 1820209090023 · tz1bmw3igCLN8N6CqgLBzJ9dyRb79E2Tdu5Q
"""

import hashlib
import json
import os
from datetime import datetime

OWNER = "Mihai Roșca"
QID = "1820209090023"
TEZOS_ADDR = "tz1bmw3igCLN8N6CqgLBzJ9dyRb79E2Tdu5Q"
LOCATION = "Spiru Haret, Brăila, România"

# ═══════════════════════════════════════════════════════════════
# REGISTRUL IP — completează/modifică denumirile aici
# Format: (cod_prescurtat, descriere, cale_fisier_sau_text)
# ═══════════════════════════════════════════════════════════════

REGISTRY = [
    # --- DOCUMENTE CONCEPTUALE ---
    ("INVARIANT-FLEET", "Invariantul Flotei Ami* - pattern arhitectural replicabil",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\INVARIANT-AMI-FLEET.md"),

    ("30-MESERII", "30 Meserii Emergente 2026-2035 - predicții BRIDGRAI",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Screenshot Claude Code\30_meserii_emergente_2026_2035.docx"),

    ("RSI-ENGINE", "RSI Hybrid Engine - Resonance Stability Index calculator",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\modules\rsi_hybrid_engine.py"),

    # --- GITHUB REPOS (înlocuiește cu ce vrei) ---
    ("UKBE-CORE", "UKBE Core Engine - REAI resonance (Kuramoto+Kalman)", "REPO:amidigiart/ukbe-core"),
    ("TVE-CORE", "Truth Vector Engine - manipulation detection", "REPO:amidigiart/tve-core"),
    ("AMIDOR-ENGINE", "Amidor Engine - dual-model anti-confabulation", "REPO:amidigiart/amidor-engine"),
    ("KINDERAGI", "KinderAGI Core - AI companion for children safety layer", "REPO:amidigiart/kinderagi-core"),
    ("TVE-UKBE-FUSION", "TVE-UKBE Fusion - combined engine", "REPO:amidigiart/tve-ukbe-fusion"),
    ("P6-ADLER", "P6 Adler Ghost Peak - bifurcation paper DOI Zenodo", "REPO:amidigiart/p6-adler-ghost-peak"),

    # --- LANDING PAGES (produse Ami*) ---
    ("AMIBELLAI", "AmiBellAI - beauty companion AI", "REPO:amidigiart/amibellai.com"),
    ("AMITHERAI", "AmiTherai - wellness companion AI", "REPO:amidigiart/amitherai.com"),
    ("AMIWEALTHAI", "AmiWealthAI - private wealth intelligence", "REPO:amidigiart/amiwealthai.com"),
    ("AMILUXAI", "AmiLuxAI - 11 AI companion ecosystem", "REPO:amidigiart/amiluxai.com"),
    ("AMIPECETAI", "AmiPecetAI - Truth Vector Engine SaaS", "REPO:amidigiart/amipecetai.com"),
    ("AMIQIAI", "AmiQiAI - energy journal ECDSA signatures", "REPO:amidigiart/amiqiai.com"),
    ("AMIAPIAPI", "AmiApiAI - API documentation companion", "REPO:amidigiart/amiapiai.com"),
    ("AMIGHOSTAI", "AmiGhostAI - ghost code & dependency audit", "REPO:amidigiart/amighostai.com"),
    ("AMIAGENTAI", "AmiAgentAI - real estate AI companion", "REPO:amidigiart/amiagentai.com"),
    ("AMIBRAINAI", "AmiBrainAI - study & learning companion", "REPO:amidigiart/amibrainai.com"),
    ("AMIORACLEAI", "AmiOracleAI - business forecast companion", "REPO:amidigiart/amioracleai.com"),
    ("ANTETAI", "AntetAI - ecosystem hub", "REPO:amidigiart/antetai.com"),

    # --- CONCEPTE IP ---
    ("SM-EQ-R", "S(M)=R Invariant Formula - Sensul precede Sintaxa",
     "TEXT:S(M)=R — Sensul precede sintaxa. Carbonul ancorează Siliciul. Mihai Rosca 2023-2026."),

    ("SHARED-AI-ENGINE", "SharedAIEngine Architecture - single backend multi-product",
     "TEXT:SharedAIEngine pattern: one AI backend serves N products via SYSTEM_PROMPTS routing. Zero duplication. Mihai Rosca 2024-2026."),

    ("FLEET-INVARIANT-TM", "Fleet Invariant Pattern TM - zero-build deployment",
     "TEXT:Single-file HTML, zero build step, zero server, GitHub Pages, full EU compliance from second one. Replicable in <5 min per product. Mihai Rosca 2026."),

    ("TRANSGENERATIONAL", "Linia Transgenerațională Mihai-Patrick Core",
     "TEXT:Priority absolută: tot ce se construiește servește linia Mihai→Patrick Roșca. Ecosistemul digital ca patrimoniu transgenerațional. 2023-2060+."),

    # --- TVE CORE v1.9 ---
    ("TVE-CORE-V19", "TVE Core Unified v1.9 - Truth Vector Engine (5 AI architects)",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\tve_core_unified_v1_9.py"),

    # ═══════════════════════════════════════════════════════════
    # PĂDUREA DE COD TM — seria de storybook-uri psihopedagogice
    # ═══════════════════════════════════════════════════════════

    # --- Din Desktop\Padurea de cod Book ---
    ("PDC-ANCORA", "Pădurea de Cod: Ancora de Aur a Invariantului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Ancora de Aur a Invariantului.pdf"),

    ("PDC-10ROLURI", "Pădurea de Cod: Arhitectul Invariantului și Cele Zece Roluri ale Viitorului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod_ Arhitectul Invariantului și Cele Zece Roluri ale Viitorului.pdf"),

    ("PDC-RADACINI", "Pădurea de Cod: Rădăcinile Memoriei",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Rădăcinile Memoriei.pdf"),

    ("PDC-CETATEA", "Pădurea de Cod: Cetatea Zorilor",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Cetatea Zorilor.pdf"),

    ("PDC-CAMERA", "Pădurea de Cod: Camera Rezonanței",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Camera Rezonanței (1).pdf"),

    ("PDC-IZVORUL", "Pădurea de Cod: Izvorul Puterii",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Izvorul Puterii.pdf"),

    ("PDC-CAPITAN", "Pădurea de Cod: Căpitanul Viitorului și Cele Zece Puteri",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod_ Căpitanul Viitorului și Cele Zece Puteri.pdf"),

    ("PDC-MOSTENIRE", "Pădurea de Cod: Moștenirea Arhitectului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Moștenirea Arhitectului.pdf"),

    ("PDC-LUMILOR", "Pădurea de Cod: Arhitectul Lumilor Viitoare",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod_ Arhitectul Lumilor Viitoare.pdf"),

    ("PDC-DANSUL", "Pădurea de Cod: Dansul Adevărului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod_ Dansul Adevărului.pdf"),

    ("PDC-PUNTI", "Pădurea de Cod: Arhitectul Marilor Punți",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Arhitectul Marilor Punți.pdf"),

    ("PDC-INSULA", "Pădurea de Cod: Insula Arhitectului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Insula Arhitectului.pdf"),

    ("PDC-NODURI", "Pădurea de Cod: Arhitectul de Noduri",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Arhitectul de Noduri.pdf"),

    ("PDC-INIMA", "Pădurea de Cod: Inima Arhitectului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Inima Arhitectului.pdf"),

    ("PDC-LUMINA", "Pădurea de Cod: Arhitectul Colector de Lumină",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod și Arhitectul Colector de Lumină.pdf"),

    ("PDC-INTRE-LUMI", "Pădurea de Cod: Arhitectul de Punți - Inima dintre Lumi",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Arhitectul de Punți_ Inima dintre Lumi.pdf"),

    ("PDC-SUVERANITATE", "Pădurea de Cod: Cetatea Suveranității - Arhitectul Viitorului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Cetatea Suveranității_ Arhitectul Viitorului.pdf"),

    ("PDC-ECHILIBRU", "Pădurea de Cod: Arhitectul Echilibrului - Dincolo de Pădurea de Cod",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Arhitectul Echilibrului_ Dincolo de Pădurea de Cod.pdf"),

    ("PDC-PECETEA", "Pădurea de Cod: Pecetea de Cristal - Arhitectul și Legătura de Aur",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pecetea de Cristal_ Arhitectul și Legătura de Aur.pdf"),

    ("PDC-SINELE", "Pădurea de Cod: Arhitectul Șinelor Viitorului",
     r"C:\Users\Patrick&Mihai\Desktop\Padurea de cod Book\Pădurea de Cod_ Arhitectul Șinelor Viitorului.pdf"),

    # --- Din Downloads (povești adiționale) ---
    ("PDC-LUPA", "Pădurea de Cod: Lupa de Invariante",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Lupa de Invariante.pdf"),

    ("PDC-FALCON", "Pădurea de Cod: Scutul Falcon",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Scutul Falcon.pdf"),

    ("PDC-HASH", "Pădurea de Cod: Căutătorul de Hash-uri",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Căutătorul de Hash-uri.pdf"),

    ("PDC-CASP", "Pădurea de Cod: Busola C.A.S.P.",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Busola C.A.S.P.pdf"),

    ("PDC-AIRGAP", "Pădurea de Cod: Scutul Air-Gap",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Scutul Air-Gap.pdf"),

    ("PDC-SIMFONIA", "Pădurea de Cod: Simfonia Rezonanței",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Simfonia Rezonanței.pdf"),

    ("PDC-TOKEN", "Pădurea de Cod: Oglinda Tokenilor",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Oglinda Tokenilor.pdf"),

    ("PDC-CASP-AGI", "Pădurea de Cod: Busola C.A.S.P. și AGI",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Busola C.A.S.P SI AGI.pdf"),

    ("PDC-KINDERAGI", "Pădurea de Cod: Inima KinderAGI",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Inima KinderAGI.pdf"),

    ("PDC-KINDERAGI-V2", "Pădurea de Cod: Inima KinderAGI (optimizat)",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Inima KinderAGI (optimizat).pdf"),

    ("PDC-AMIDOR", "Pădurea de Cod: Cumpăna AmiDor",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Cumpăna AmiDor.pdf"),

    ("PDC-CAMERA-V2", "Pădurea de Cod: Camera Rezonanței (v2)",
     r"C:\Users\Patrick&Mihai\Downloads\Padurea de cod TM\Pădurea de Cod și Camera Rezonanței.pdf"),

    # ═══════════════════════════════════════════════════════════
    # NOVA ȘI CEI 12 PILONI — seria educativă complementară
    # ═══════════════════════════════════════════════════════════

    ("NOVA-P01", "Nova și Primul Pilon al Viitorului",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Primul Pilon al Viitorului.pdf"),

    ("NOVA-P02", "Nova și Pilonul Curiozității",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Pilonul Curiozității.pdf"),

    ("NOVA-P03", "Nova și Pilonul Empatiei",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Pilonul Empatiei.pdf"),

    ("NOVA-P04", "Nova și Pilonul Gândirii Critice",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Pilonul Gândirii Critice.pdf"),

    ("NOVA-P05", "Nova și Pilonul Alfabetizării Digitale",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Pilonul Alfabetizării Digitale.pdf"),

    ("NOVA-P06", "Nova și Pilonul Conștiinței Ecologice",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Pilonul Conștiinței Ecologice.pdf"),

    ("NOVA-P07", "Nova și Pilonul Colaborării Globale",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Pilonul Colaborării Globale.pdf"),

    ("NOVA-P08", "Nova și Simfonia Creativității Digitale",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Simfonia Creativității Digitale.pdf"),

    ("NOVA-P09", "Nova și Arhitectura Echilibrului - Al Nouălea Pilon",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Arhitectura Echilibrului_ Al Nouălea Pilon.pdf"),

    ("NOVA-P10", "Nova și Arhitectura Evoluției - Al Zecelea Pilon",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Arhitectura Evoluției_ Al Zecelea Pilon.pdf"),

    ("NOVA-P11", "Nova și Arhitectura Responsabilității - Al Unsprezecelea Pilon",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Arhitectura Responsabilității_ Al Unsprezecelea Pilon.pdf"),

    ("NOVA-P12", "Nova și Cei Doisprezece Piloni: Arhitecții Viitorului",
     r"C:\Users\Patrick&Mihai\Desktop\bridgrai hub mercury\Nova și Cei Doisprezece Piloni_ Arhitecții Viitorului.pdf"),

    # --- CONCEPT: seria Pădurea de Cod TM ca întreg ---
    ("PDC-SERIA-TM", "Pădurea de Cod TM - seria completă storybook psihopedagogic (Mihai Roșca)",
     "TEXT:Pădurea de Cod TM — serie de 30+ storybook-uri psihopedagogice + 12 povești Nova. Concepte tehnice (blockchain, hash, criptografie, invariant, entropie, AI) predate prin narativă emoțională tată-fiu. Autor: Mihai Roșca, fost învățător cu definitivat (Universitatea Ovidius, Constanța). Destinatar primar: Patrick Roșca (~9 ani). 2024-2026."),

    # ═══════════════════════════════════════════════════════════
    # ARHIVE CREATIVE & R&D — Foldere create (22 iul 2026)
    # Hash-uite pe baza _CATALOG.md verificabil din fiecare folder
    # ═══════════════════════════════════════════════════════════

    ("DREAMSCAPE-ARCHIVE", "The Digital Dreamscape - arhivă AI art multi-model (11 generatoare, 1301 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\the digital dreamscape\_CATALOG.md"),

    ("ALPHAPURE-ARCHIVE", "UNKNOWN/Claude pilar 12 - AlphaPure Fortress + HASN + R&D (457 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\UNKNOWN\_CATALOG.md"),

    ("NIGHTCAFE-STUDIO", "NightCafe AI Art Studio - colecție primară + quantum series (923 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\NightCafe\_CATALOG.md"),

    ("NVIDIA-LEARNING", "Nvidia DLI Learning Hub - Python/ML/quantum training (545 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\Nvidia\_CATALOG.md"),

    ("NCRB-PIPELINE", "NC RB - NightCafe→Redbubble pipeline + DeepSeek code (393 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\NC RB\_CATALOG.md"),

    ("NFT-AGI-HUB", "NFT & AGI Development Hub - KinderAGI MVP + Continuum (326 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\NFT\_CATALOG.md"),

    ("NEWRB-STORE", "New Redbubble Store - AGI Soulforge + BRIDGRAI Hub (94 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\new RB\_CATALOG.md"),

    ("REDBUBBLE-ART", "Redbubble Original Art Store - Gemini + nature/cosmic (68 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\redbubble\_CATALOG.md"),

    ("PROMPT-SECURITY", "Prompt System Leaks - AI security research 26 system prompts (54 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\prompt system leaks\_CATALOG.md"),

    ("KIMI-PROTOTYPES", "Kimi/Moonshot AI Prototyping Session - DeepSeek scripts (31 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\kimi files\_CATALOG.md"),

    ("KOTSU-QUANTUM", "Kotsu Files - Quantum IoT Chatbot + React/TS prototypes (68 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\kotsu files\_CATALOG.md"),

    ("AMIGENOME-PLATFORM", "Amigenome Genomic Analysis Platform - Python backend complet (21 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\Amigenome\_CATALOG.md"),

    ("GENESIS-NFT", "BRIDGRAI Genesis NFT - Solidity contract + whitepaper (15 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\RB 3 sept. 2025\_CATALOG.md"),

    ("YOUTUBE-CHANNEL", "Sabrina YouTube Channel Assets - BRIDGRAI guide + mind map (13 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\Sabrina YouTube\_CATALOG.md"),

    ("SERENITY-CITADEL", "Serenity Citadel Platform - deploy package + CV blueprint (9 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\Serenity chat\_CATALOG.md"),

    ("ALPHA-VISUAL", "Ce ai creat Mihai Alpha - documentație vizuală faza Alpha (8 fișiere)",
     r"C:\Users\Patrick&Mihai\Desktop\Foldere create\Ce ai creat, Mihai_Alpha\_CATALOG.md"),
]


def hash_file(path: str) -> str:
    """SHA-256 hash al unui fișier."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_text(text: str) -> str:
    """SHA-256 hash al unui text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_manifest():
    """Generează manifestul complet cu hash-uri."""
    manifest = {
        "version": "2.0.0",
        "owner": OWNER,
        "qid": QID,
        "tezos_address": TEZOS_ADDR,
        "location": LOCATION,
        "generated": datetime.utcnow().isoformat() + "Z",
        "entries": [],
    }

    print("=" * 60)
    print(f"  TEZOS IP REGISTRY — Hash Generation")
    print(f"  Owner: {OWNER} · QID: {QID}")
    print(f"  Address: {TEZOS_ADDR}")
    print("=" * 60)
    print()

    for code, description, source in REGISTRY:
        entry = {
            "code": code,
            "description": description,
            "source_type": None,
            "sha256": None,
        }

        if source.startswith("REPO:"):
            repo_name = source[5:]
            content = f"GITHUB_REPO:{repo_name}:OWNER:{TEZOS_ADDR}:DATE:{datetime.utcnow().date().isoformat()}"
            entry["sha256"] = hash_text(content)
            entry["source_type"] = "github_repo"
            entry["repo"] = repo_name

        elif source.startswith("TEXT:"):
            text = source[5:]
            entry["sha256"] = hash_text(text)
            entry["source_type"] = "concept_text"

        else:
            # File path
            if os.path.exists(source):
                entry["sha256"] = hash_file(source)
                entry["source_type"] = "local_file"
                entry["file_size"] = os.path.getsize(source)
            else:
                entry["sha256"] = "FILE_NOT_FOUND"
                entry["source_type"] = "missing"
                print(f"  ⚠ MISSING: {source}")

        manifest["entries"].append(entry)
        status = "✓" if entry["sha256"] != "FILE_NOT_FOUND" else "✗"
        print(f"  {status} [{code:.<20s}] {entry['sha256'][:16]}...")

    # Master hash (hash of all hashes — single proof for entire portfolio)
    all_hashes = "|".join(e["sha256"] for e in manifest["entries"] if e["sha256"] != "FILE_NOT_FOUND")
    manifest["master_hash"] = hash_text(all_hashes)

    print()
    print(f"  MASTER HASH: {manifest['master_hash']}")
    print(f"  Total entries: {len(manifest['entries'])}")
    print("=" * 60)

    return manifest


if __name__ == "__main__":
    manifest = generate_manifest()

    # Save manifest
    output_path = os.path.join(os.path.dirname(__file__), "ip_manifest.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n  Manifest salvat: {output_path}")
    print(f"  Următorul pas: deploy smart contract + înregistrare on-chain")
    print(f"  Folosește master_hash pentru o singură tranzacție (ieftin)")
    print(f"  SAU înregistrează fiecare entry individual (complet)")
