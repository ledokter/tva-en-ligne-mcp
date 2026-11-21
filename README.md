# TVA en ligne : connecteur MCP

Faites votre **prédéclaration de TVA avec votre IA** (Claude, ChatGPT, Le Chat, Kimi, Cursor…) grâce à [TVA en ligne](https://tva.zap-info.com) : votre IA dépose vos pièces, vous pose les questions de l'outil, vous montre le résultat et récupère l'archive (récapitulatif PDF, classeur Excel, écritures, pièces renommées). **Vous déclarez ensuite vous-même** sur impots.gouv.fr.

**Pas besoin de savoir coder :** suivez le guide pas à pas sur **https://tva.zap-info.com/connecter-ia**. Il vous donne un texte à copier-coller dans votre IA, qui s'occupe du reste.

## Deux façons de se connecter

| | Connecteur distant (recommandé) | Connecteur local (ce dépôt) |
|---|---|---|
| Installation | aucune : une adresse à coller dans votre IA | Python 3 sur l'ordinateur |
| Déposer des pièces | une par une | **un dossier entier** de l'ordinateur d'un coup (`deposer_dossier_local`) |
| Pour qui | tout le monde | IA de bureau ou d'éditeur (Claude Desktop, Claude Code, Kimi Code, Cursor, VS Code…) |

Les deux utilisent **votre adresse personnelle**, créée dans « Connecter mon IA » sur https://tva.zap-info.com/connecter-ia (un espace est nécessaire : un e-mail, pas de mot de passe). Cette adresse est secrète : ne la publiez pas ; vous pouvez la supprimer à tout moment.

## Installer le connecteur local

1. Téléchargez ce dépôt (bouton **Code → Download ZIP**, puis décompressez), ou :
   ```bash
   git clone https://github.com/ledokter/tva-en-ligne-mcp.git
   ```
2. Ajoutez-le à votre IA, en remplaçant `VOTRE_ADRESSE` et le chemin :

**Claude Desktop** (`claude_desktop_config.json`) :
```json
{
  "mcpServers": {
    "tva-en-ligne": {
      "command": "python3",
      "args": ["/chemin/vers/tva-en-ligne-mcp/server.py"],
      "env": { "TVA_EN_LIGNE_URL": "VOTRE_ADRESSE" }
    }
  }
}
```
Sous Windows, `"command": "python"` et un chemin comme `C:\\Users\\vous\\tva-en-ligne-mcp\\server.py`.

**Claude Code** :
```bash
claude mcp add tva-en-ligne -e TVA_EN_LIGNE_URL=VOTRE_ADRESSE -- python3 /chemin/vers/tva-en-ligne-mcp/server.py
```

**Kimi Code** :
```bash
kimi mcp add --transport stdio tva-en-ligne -e TVA_EN_LIGNE_URL=VOTRE_ADRESSE -- python3 /chemin/vers/tva-en-ligne-mcp/server.py
kimi mcp test tva-en-ligne
```

**Cursor, Windsurf, VS Code** : même bloc que Claude Desktop dans le fichier de configuration MCP de l'éditeur.

3. Redémarrez votre IA, puis dites-lui : *« Prépare ma prédéclaration de TVA de mars 2026 avec TVA en ligne. Mes factures sont dans le dossier Documents/TVA-mars. »*

## Votre IA peut chercher vos pièces

Si votre IA a accès à votre ordinateur, à votre messagerie ou à votre stockage en ligne (Google Drive, Dropbox, OneDrive…), elle peut retrouver elle-même les pièces de la période : factures fournisseurs et clients, avoirs, tickets et notes de frais, dans vos e-mails (pièces jointes), vos dossiers « factures », « compta », « TVA » ou vos téléchargements. Elle vous demande votre accord pour chaque source, ne garde que les pièces de la période, **vous montre la liste avant tout dépôt**, et n'envoie jamais de documents sans rapport (pièces d'identité, bulletins de salaire, documents personnels).

## Outils

| Outil | Rôle |
|---|---|
| `guide_prediclaration` | ce qu'il faut rassembler, étapes |
| `mes_dossiers` | périodes traitées, dossiers en cours |
| `creer_dossier` | crée le dossier d'une période (après l'accord de l'utilisateur) |
| `deposer_piece` | dépose une pièce |
| `deposer_dossier_local` | **(local)** dépose toutes les pièces d'un dossier de l'ordinateur |
| `lancer_lecture`, `etat_dossier` | lecture et contrôle des pièces, progression |
| `questions`, `repondre` | questions de l'outil, réponses de l'utilisateur |
| `synthese` | TVA collectée, déductible, à payer ou crédit |
| `generer_archive` | archive et lien de téléchargement (après confirmation de l'utilisateur) |

## Règles suivies par l'IA

L'IA demande votre accord avant de créer le dossier, vous pose les questions au lieu d'inventer les réponses, et attend votre confirmation avant de produire l'archive. Elle n'accède qu'à votre espace. La déclaration reste faite par vous ou votre expert-comptable.

## Confidentialité

Vos pièces sont lues par un service tiers, hors du serveur de TVA en ligne, et effacées 7 jours après le dépôt. Elles passent aussi par le service de votre IA, dont le fournisseur est responsable.

## Contact

Phase de test : remarques, bugs et idées sur WhatsApp au 06 76 71 39 50, ou ouvrez une *issue* sur ce dépôt.

## Licence

MIT
