# AeroSafe — Diagramme de séquence

> Scénario principal : **collecte des données de vol → application des règles → génération et enregistrement d'une alerte.**
> Cohérent avec le diagramme de classes (`classes.md`). Rendu automatique sur GitHub ; édition/export : https://mermaid.live

```mermaid
sequenceDiagram
    autonumber
    participant Sys as Tâche périodique
    participant Col as CollecteurOpenSky
    participant API as OpenSky API
    participant Av as Aeronef
    participant Moteur as MoteurRegles
    participant R as Regle (R1..R5)
    participant Depot as DepotAlertes
    participant DB as PostgreSQL

    Note over Sys: Le système surveille en continu

    %% --- 1. Collecte ---
    Sys->>Col: recuperer_etats()
    Col->>API: GET /states/all (zone surveillée)
    API-->>Col: états bruts (JSON)
    Col->>Av: ajouter_etat(EtatVol)
    Col-->>Sys: liste d'Aeronef

    %% --- 2. Application des règles ---
    Sys->>Moteur: analyser(aeronef)
    loop pour chaque Regle (R1 à R5)
        Moteur->>R: evaluer(aeronef)
        alt seuil dépassé
            R-->>Moteur: Alerte
        else rien d'anormal
            R-->>Moteur: null
        end
    end
    Moteur-->>Sys: liste d'Alertes

    %% --- 3. Enregistrement (sans doublon) ---
    loop pour chaque Alerte
        Sys->>Depot: existe_deja(alerte) ?
        alt nouvelle alerte
            Depot->>DB: INSERT alerte
            DB-->>Depot: OK
            Depot-->>Sys: alerte enregistrée
        else doublon
            Depot-->>Sys: ignorée
        end
    end
```

## Lecture du scénario

1. **Collecte** (étapes 1-5) : la tâche périodique demande au `CollecteurOpenSky` de récupérer les données ; celui-ci interroge l'**API OpenSky**, puis construit/alimente les `Aeronef` avec leurs `EtatVol`.
2. **Détection** (étapes 6-12) : le `MoteurRegles` applique **chaque** règle R1→R5 sur l'aéronef (`evaluer()`). Chaque règle renvoie une `Alerte` si son seuil est dépassé, sinon `null`.
3. **Enregistrement** (étapes 13+) : pour chaque alerte, `DepotAlertes` vérifie d'abord `existe_deja()` pour **éviter les doublons** (critère #22), puis insère en base PostgreSQL.

## Légende des symboles

| Symbole | Signification |
|---|---|
| `->>` | message / appel synchrone (A appelle B) |
| `-->>` | réponse / retour de valeur |
| `loop` | répétition (ici : sur chaque règle, puis sur chaque alerte) |
| `alt / else` | embranchement conditionnel (selon que le seuil est dépassé ou non) |
| `autonumber` | numérote les étapes automatiquement |

## Cohérence avec le diagramme de classes

Chaque flèche correspond à une **méthode** du diagramme de classes :
`recuperer_etats()`, `ajouter_etat()`, `analyser()`, `evaluer()`, `existe_deja()`, `enregistrer()`.
Le diagramme de séquence montre **dans quel ordre** ces méthodes s'appellent dans le temps — là où le diagramme de classes montre seulement la structure.
