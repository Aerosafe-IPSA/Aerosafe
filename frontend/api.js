/**
 * Client de l'API AeroSafe, commun à toutes les pages.
 *
 * Il garde le jeton reçu à la connexion et l'envoie avec chaque requête.
 * Exemple : const api = new ClientApi(); const avions = await api.appeler("/aircraft?q=afr");
 */
class ClientApi {
  constructor() {
    this.cleJeton = "aerosafe.jeton";
    this.pageConnexion = "login.html";
  }

  /** Jeton de la personne connectée, ou null. */
  get jeton() {
    return sessionStorage.getItem(this.cleJeton);
  }

  /**
   * Connecte la personne et enregistre son jeton.
   * Renvoie son compte ({email, role}), ou null si les identifiants sont faux.
   */
  async connecter(email, motDePasse) {
    const reponse = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, mot_de_passe: motDePasse }),
    });
    if (!reponse.ok) {
      return null;
    }
    const donnees = await reponse.json();
    sessionStorage.setItem(this.cleJeton, donnees.access_token);
    return this.appeler("/me");
  }

  /** Oublie le jeton et revient à la page de connexion. */
  deconnecter() {
    sessionStorage.removeItem(this.cleJeton);
    window.location.href = this.pageConnexion;
  }

  /**
   * Appelle une route de l'API et renvoie sa réponse (objet ou liste).
   * Sans jeton valide, renvoie vers la page de connexion.
   * Renvoie null si la ressource n'existe pas (404).
   */
  async appeler(chemin) {
    if (!this.jeton) {
      this.deconnecter();
      return null;
    }
    const reponse = await fetch(chemin, {
      headers: { Authorization: "Bearer " + this.jeton },
    });
    if (reponse.status === 401) {
      this.deconnecter();
      return null;
    }
    if (reponse.status === 404) {
      return null;
    }
    if (!reponse.ok) {
      throw new Error("Erreur de l'API (" + reponse.status + ") sur " + chemin);
    }
    return reponse.json();
  }

  /**
   * Vérifie qu'une personne est connectée et renvoie son compte.
   * À appeler au chargement de chaque page protégée. Si un rôle est exigé
   * et que le compte ne l'a pas, renvoie vers la recherche.
   */
  async exigerConnexion(roleExige) {
    const compte = await this.appeler("/me");
    if (compte && roleExige && compte.role !== roleExige) {
      window.location.href = "recherche.html";
      return null;
    }
    return compte;
  }
}
