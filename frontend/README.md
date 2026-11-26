# Frontend

Interface web : connexion, recherche, fiche avion et tableau de bord (carte Leaflet).

Les pages sont servies par l'API, sous `/app`. Une fois l'API lancée (`uvicorn backend.main:app --reload`), ouvrir http://127.0.0.1:8000/ : la racine renvoie vers la page de connexion.

## Appeler l'API depuis une page

Toutes les pages utilisent la classe `ClientApi` de `api.js`, qui envoie le jeton de connexion avec chaque requête :

```html
<script src="api.js"></script>
<script>
const api = new ClientApi();

async function afficher() {
  const compte = await api.exigerConnexion();
  const avions = await api.appeler("/aircraft?q=afr");
}

afficher();
</script>
```

| Méthode | Rôle |
|---|---|
| `connecter(email, motDePasse)` | Connecte la personne ; renvoie son compte (`email`, `role`) ou `null` si les identifiants sont faux |
| `exigerConnexion(role)` | À appeler au chargement d'une page protégée ; renvoie vers la connexion sans jeton valide |
| `appeler(chemin)` | Appelle une route de l'API ; renvoie `null` si la ressource n'existe pas |
| `deconnecter()` | Oublie le jeton et revient à la connexion |

Aucun mot de passe ne doit figurer dans une page : la vérification se fait côté serveur, par `POST /login`.
