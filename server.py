#!/usr/bin/env python3
"""Connecteur MCP local de « TVA en ligne » (https://tva.zap-info.com).

Relais stdio -> MCP distant de TVA en ligne, avec un outil en plus :
deposer_dossier_local, qui dépose d'un coup toutes les pièces d'un dossier de l'ordinateur.

Python 3.8+ uniquement, aucune dépendance. Variable obligatoire :
  TVA_EN_LIGNE_URL = votre adresse personnelle (https://tva.zap-info.com/mcp/…),
  créée sur https://tva.zap-info.com/connecter-ia
"""
import base64, json, os, sys, urllib.error, urllib.request

URL = os.environ.get("TVA_EN_LIGNE_URL", "").strip()
EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".xml", ".zip"}
MAX_FICHIER = 10 * 1024 * 1024
MAX_FICHIERS = 300
VERSION = "1.0.0"

OUTIL_LOCAL = {
    "name": "deposer_dossier_local",
    "description": ("Dépose toutes les pièces d'un dossier de l'ordinateur de l'utilisateur (PDF, JPG, PNG, WEBP, XML, ZIP ; "
                    "sous-dossiers compris ; 10 Mo par fichier, 300 fichiers). Les noms des sous-dossiers (clients, fournisseurs, frais…) "
                    "aident au classement. Demander à l'utilisateur quel dossier déposer ; ne jamais parcourir d'autres dossiers."),
    "inputSchema": {"type": "object", "additionalProperties": False, "required": ["dossier_id", "chemin_local"], "properties": {
        "dossier_id": {"type": "string", "description": "Identifiant du dossier TVA en ligne (créé avec creer_dossier)"},
        "chemin_local": {"type": "string", "description": "Chemin du dossier sur l'ordinateur, indiqué par l'utilisateur"}}},
}

_id = [0]


def distant(methode, params=None):
    """Appel JSON-RPC au MCP distant."""
    _id[0] += 1
    corps = json.dumps({"jsonrpc": "2.0", "id": _id[0], "method": methode, "params": params or {}}).encode()
    req = urllib.request.Request(URL, corps, {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                                              "User-Agent": "tva-en-ligne-mcp/" + VERSION})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:300]
        return {"error": {"code": -32000, "message": f"TVA en ligne a répondu {e.code} : {msg}"}}
    except Exception as e:  # réseau
        return {"error": {"code": -32000, "message": f"TVA en ligne injoignable : {e}"}}


def texte(t, erreur=False):
    return {"content": [{"type": "text", "text": t}], "isError": erreur}


def deposer_dossier_local(args):
    dossier_id = str(args.get("dossier_id", "")).strip()
    racine = os.path.abspath(os.path.expanduser(str(args.get("chemin_local", "")).strip()))
    if not os.path.isdir(racine):
        return texte(f"Dossier introuvable : {racine}", True)
    fichiers = []
    for base, sous, noms in os.walk(racine):
        sous[:] = [s for s in sous if not s.startswith(".")]
        for n in sorted(noms):
            if n.startswith(".") or os.path.splitext(n)[1].lower() not in EXTENSIONS:
                continue
            fichiers.append(os.path.join(base, n))
    if not fichiers:
        return texte("Aucune pièce trouvée (PDF, JPG, PNG, WEBP, XML, ZIP).", True)
    if len(fichiers) > MAX_FICHIERS:
        return texte(f"{len(fichiers)} fichiers : {MAX_FICHIERS} au plus par dossier.", True)
    deposes, ignores = 0, []
    for f in fichiers:
        rel = os.path.relpath(f, racine).replace(os.sep, "/")
        if os.path.getsize(f) > MAX_FICHIER:
            ignores.append(f"{rel} (plus de 10 Mo)")
            continue
        with open(f, "rb") as h:
            contenu = base64.b64encode(h.read()).decode()
        r = distant("tools/call", {"name": "deposer_piece", "arguments": {
            "dossier_id": dossier_id, "nom_fichier": os.path.basename(f), "chemin": rel, "contenu_base64": contenu}})
        res = r.get("result") or {}
        if r.get("error") or res.get("isError"):
            detail = (r.get("error") or {}).get("message") or res.get("content", [{}])[0].get("text", "")
            ignores.append(f"{rel} ({detail[:120]})")
        else:
            deposes += 1
    bilan = f"{deposes} pièce(s) déposée(s) depuis {racine}."
    if ignores:
        bilan += " Non déposées : " + " ; ".join(ignores[:20])
    return texte(bilan + " Étape suivante : lancer_lecture.", deposes == 0)


def repondre(id_, resultat=None, erreur=None):
    m = {"jsonrpc": "2.0", "id": id_}
    m["error" if erreur else "result"] = erreur or resultat
    sys.stdout.write(json.dumps(m, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    for ligne in sys.stdin:
        ligne = ligne.strip()
        if not ligne:
            continue
        try:
            req = json.loads(ligne)
        except json.JSONDecodeError:
            continue
        id_, methode, params = req.get("id"), req.get("method", ""), req.get("params") or {}
        if id_ is None:  # notification
            continue
        if not URL.startswith("https://"):
            repondre(id_, erreur={"code": -32000, "message": "Variable TVA_EN_LIGNE_URL manquante : créez votre adresse sur https://tva.zap-info.com/connecter-ia"})
            continue
        if methode == "initialize":
            r = distant("initialize", params)
            res = r.get("result") or {}
            repondre(id_, {"protocolVersion": params.get("protocolVersion", "2025-06-18"), "capabilities": {"tools": {"listChanged": False}},
                           "serverInfo": {"name": "tva-en-ligne-local", "title": "TVA en ligne", "version": VERSION},
                           "instructions": (res.get("instructions") or "") + "\nOutil local en plus : deposer_dossier_local (dossier de l'ordinateur indiqué par l'utilisateur)."})
        elif methode == "ping":
            repondre(id_, {})
        elif methode == "tools/list":
            r = distant("tools/list")
            if r.get("error"):
                repondre(id_, erreur=r["error"])
            else:
                repondre(id_, {"tools": r["result"]["tools"] + [OUTIL_LOCAL]})
        elif methode == "tools/call":
            if params.get("name") == "deposer_dossier_local":
                repondre(id_, deposer_dossier_local(params.get("arguments") or {}))
            else:
                r = distant("tools/call", params)
                repondre(id_, r.get("result"), r.get("error"))
        else:
            repondre(id_, erreur={"code": -32601, "message": "méthode inconnue : " + methode})


if __name__ == "__main__":
    main()
