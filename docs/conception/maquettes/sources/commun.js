// Éléments partagés par les maquettes : en-tête, carte stylisée et données fictives.

const ICONE_AVION = `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15.5v-2l-8-5V3.2a1.5 1.5 0 0 0-3 0v5.3l-8 5v2l8-2.5v5.2l-2 1.5V21l3.5-1 3.5 1v-1.3l-2-1.5V13z"/></svg>`;

function entete(role, actif) {
  const pages = role === "Superviseur" ? ["Dashboard", "Recherche", "Règles"] : ["Recherche"];
  const nav = pages.map(p => `<span class="${p === actif ? "actif" : ""}">${p}</span>`).join("");
  const nom = role === "Superviseur" ? "superviseur.demo" : "utilisateur.demo";
  document.body.insertAdjacentHTML("afterbegin", `
    <header class="entete">
      <div class="marque">${ICONE_AVION}AeroSafe</div>
      <nav class="nav">${nav}</nav>
      <div class="compte"><span>01/11/2026 · 14:35</span><b>${nom}</b><span class="badge-role">${role}</span><span>Déconnexion</span></div>
    </header>`);
}

function pied(ecran) {
  document.body.insertAdjacentHTML("beforeend", `
    <footer class="pied"><span>Maquette AeroSafe · ${ecran}</span><span>Données fictives · issue #13</span></footer>`);
}

// Contours simplifiés, en [longitude, latitude].
const FRANCE = [[2.55,51.08],[1.6,50.87],[1.58,50.2],[0.2,49.7],[0.1,49.5],[-1.1,49.35],[-1.25,49.7],[-1.9,49.7],[-1.6,48.65],[-3,48.8],[-4.75,48.4],[-4.4,47.85],[-2.5,47.3],[-2.1,46.8],[-1.15,46.1],[-1.25,45.5],[-1.2,44.6],[-1.75,43.37],[-0.7,42.85],[0.7,42.7],[1.75,42.45],[3.15,42.45],[3,43.1],[3.5,43.3],[4.6,43.4],[5.4,43.2],[6.2,43.05],[7,43.5],[7.5,43.78],[7,44.2],[6.9,45.1],[7.1,45.9],[6.1,46.3],[7.5,47.6],[8.2,48.95],[6.2,49.5],[4.8,50.1],[4.2,50.3]];
const CORSE = [[9.4,43],[9.55,42.2],[9.25,41.4],[8.75,41.6],[8.6,42.3],[9,42.7]];
const VOISINS = [
  [[2.55,51.08],[3.4,51.45],[3.8,52],[10.5,52],[10.5,44],[8.9,44.4],[8.2,43.95],[7.5,43.78],[5,45],[4,49]],
  [[-6.5,43.5],[-3.8,43.5],[-1.75,43.37],[-0.7,42.85],[1.75,42.45],[3.15,42.45],[3.2,41.9],[2.2,41.3],[1.2,41],[-6.5,41]],
  [[-6.5,49.9],[-3.5,50.3],[-1.3,50.7],[1.4,51.15],[1.6,51.45],[1.2,52],[-6.5,52]],
];
const VILLES = [["Paris",2.35,48.85],["Lille",3.06,50.63],["Nantes",-1.55,47.22],["Bordeaux",-0.58,44.84],["Toulouse",1.44,43.6],["Marseille",5.37,43.3],["Lyon",4.84,45.76],["Strasbourg",7.75,48.58]];

// Vue = zone de longitude/latitude affichée, largeur en pixels.
function projection(vue, largeur) {
  const echelle = largeur / (vue.lonMax - vue.lonMin);
  const ratio = Math.cos((vue.latMin + vue.latMax) / 2 * Math.PI / 180);
  const hauteur = (vue.latMax - vue.latMin) / ratio * echelle;
  return {
    hauteur,
    x: lon => (lon - vue.lonMin) * echelle,
    y: lat => (vue.latMax - lat) / ratio * echelle,
  };
}

function fondCarte(vue, largeur) {
  const p = projection(vue, largeur);
  const poly = pts => pts.map(([lon, lat]) => `${p.x(lon).toFixed(1)},${p.y(lat).toFixed(1)}`).join(" ");
  const voisins = VOISINS.map(v => `<polygon points="${poly(v)}" fill="#e9ebe5" stroke="#d3d7d0"/>`).join("");
  const villes = VILLES.map(([nom, lon, lat]) => `
    <circle cx="${p.x(lon)}" cy="${p.y(lat)}" r="2.2" fill="#8d96a0"/>
    <text x="${p.x(lon) + 5}" y="${p.y(lat) + 4}" font-size="11" fill="#6c7682">${nom}</text>`).join("");
  return {
    p,
    svg: `${voisins}
      <polygon points="${poly(FRANCE)}" fill="#fbfbf7" stroke="#b9c0b8"/>
      <polygon points="${poly(CORSE)}" fill="#fbfbf7" stroke="#b9c0b8"/>
      ${villes}`,
  };
}

const avion = (x, y, cap, couleur, taille = 1) =>
  `<path d="M0,-6 L4,5 L0,3 L-4,5 Z" transform="translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${cap}) scale(${taille})" fill="${couleur}"/>`;

// Vol AFR1462 : un point par minute de 14:05 à 14:35 (31 relevés).
const VOL = {
  altitude: Array.from({ length: 31 }, (_, i) => i < 26 ? 10668 : [10640, 9536, 9300, 9160, 9144][i - 26]),
  vitesse: Array.from({ length: 31 }, (_, i) => i < 27 ? 236 + [0, 1, 0, -1][i % 4] : [233, 230, 229, 228][i - 27]),
  cap: Array.from({ length: 31 }, (_, i) => 200 + [0, 1, 0, -1, 0, 1][i % 6]),
  position: i => [2.1 - 1.9 * i / 30, 47.6 - 3.6 * i / 30],
};
const INDICE_ALERTE = 27; // 14:32

const ALERTES = [
  { heure: "14:33", avion: "AFR1095", regle: "R1", message: "Délai trop long depuis le dernier contact", valeur: "5 min 12 s", seuil: "5 min", lon: 4.2, lat: 46.6, cap: 170 },
  { heure: "14:32", avion: "AFR1462", regle: "R3", message: "Variation importante d'altitude", valeur: "18,4 m/s", seuil: "15 m/s", lon: 0.2, lat: 44, cap: 200 },
  { heure: "14:27", avion: "RYR8GH", regle: "R5", message: "Changement important de direction", valeur: "62°", seuil: "45°", lon: -1.6, lat: 47.9, cap: 110 },
  { heure: "14:21", avion: "DLH95C", regle: "R4", message: "Variation importante de vitesse", valeur: "58 m/s", seuil: "51 m/s", lon: 6.3, lat: 48.2, cap: 250 },
  { heure: "14:18", avion: "BAW304", regle: "R2", message: "Position devenue trop ancienne", valeur: "10 min 35 s", seuil: "10 min", lon: 1.8, lat: 49.7, cap: 160 },
];

function courbe(cible, valeurs, { unite, min, max }) {
  const L = 528, H = 140, g = 44, b = 20, h = 6;
  const x = i => g + i * (L - g - 4) / (valeurs.length - 1);
  const y = v => h + (max - v) / (max - min) * (H - h - b);
  const trace = valeurs.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const fmt = v => v.toLocaleString("fr-FR");
  const ancrage = i => i === 0 ? "start" : i === 30 ? "end" : "middle";
  const graduations = [0, 10, 20, 30].map(i =>
    `<text x="${x(i)}" y="${H - 4}" font-size="11" fill="#5a6878" text-anchor="${ancrage(i)}">14:${String(5 + i).padStart(2, "0")}</text>`).join("");
  document.getElementById(cible).innerHTML = `
    <line x1="${g}" x2="${L}" y1="${y(max)}" y2="${y(max)}" stroke="#dde3ea"/>
    <line x1="${g}" x2="${L}" y1="${y(min)}" y2="${y(min)}" stroke="#dde3ea"/>
    <text x="${g - 6}" y="${y(max) + 4}" font-size="11" fill="#5a6878" text-anchor="end">${fmt(max)}</text>
    <text x="${g - 6}" y="${y(min) + 4}" font-size="11" fill="#5a6878" text-anchor="end">${fmt(min)}</text>
    <line x1="${x(INDICE_ALERTE)}" x2="${x(INDICE_ALERTE)}" y1="${h}" y2="${H - b}" stroke="#c0342b" stroke-dasharray="3 3"/>
    <text x="${x(INDICE_ALERTE) - 5}" y="${h + 10}" font-size="11" font-weight="700" fill="#c0342b" text-anchor="end">R3</text>
    <path d="${trace}" fill="none" stroke="#12355b" stroke-width="2"/>
    <circle cx="${x(valeurs.length - 1)}" cy="${y(valeurs[valeurs.length - 1])}" r="3" fill="#12355b"/>
    ${graduations}`;
}
