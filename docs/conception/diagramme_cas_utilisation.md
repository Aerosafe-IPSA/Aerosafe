# AeroSafe — Diagramme de cas d'utilisation

> Reproduction du diagramme du cahier des charges, en Mermaid (versionnable).
> Sur GitHub, le rendu s'affiche automatiquement. Pour éditer/exporter : https://mermaid.live

```mermaid
flowchart LR
    %% --- Acteurs ---
    Util(("👤 Utilisateur"))
    Sup(("👤 Superviseur"))
    OSN(("🛰️ OpenSky Network<br/>«système externe»"))

    %% Le superviseur hérite des droits de l'utilisateur
    Sup -. "généralisation" .-> Util

    %% --- Cas d'utilisation : Superviseur ---
    Sup --> UC_Dash([Accéder au dashboard global])
    Sup --> UC_Conf([Configurer les règles métier R1-R5])
    Sup --> UC_Stats([Consulter les statistiques globales])
    Sup --> UC_Gerer([Gérer les alertes - filtrer / acquitter])

    %% --- Cas d'utilisation : Utilisateur ---
    Util --> UC_Param([Consulter les paramètres de vol])
    Util --> UC_Traj([Visualiser la trajectoire sur carte interactive])
    Util --> UC_Rech([Rechercher un aéronef par ICAO24])
    Util --> UC_AlAero([Consulter les alertes d'un aéronef])

    %% --- Cas d'utilisation internes ---
    UC_Recup([Récupérer les données de vol - OpenSky API])
    UC_Moteur([Appliquer le moteur de règles métier])
    UC_Alerte([Générer et enregistrer une alerte])

    %% Le système externe alimente la récupération de données
    OSN --> UC_Recup

    %% --- Relations «include» ---
    UC_Param  -. include .-> UC_Recup
    UC_Traj   -. include .-> UC_Recup
    UC_Rech   -. include .-> UC_Recup
    UC_Recup  -. include .-> UC_Moteur
    UC_Moteur -. include .-> UC_Alerte
    UC_Gerer  -. include .-> UC_Alerte
    UC_AlAero -. include .-> UC_Alerte
```

## Légende

| Élément | Signification |
|---|---|
| 👤 Acteur | Personne ou système qui interagit avec AeroSafe |
| `([ ... ])` | Un cas d'utilisation (une action possible) |
| `«include»` | Un cas en inclut **toujours** un autre (dépendance obligatoire) |
| `généralisation` | Le Superviseur peut faire **tout** ce que l'Utilisateur fait, **+** ses actions propres |
