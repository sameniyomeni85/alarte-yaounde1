import os
from flask import Flask, request, redirect, url_for
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# Base de donnees temporaire
alertes = [
    {"id": 1, "quartier": "Biyem-Assi", "type": "Electricite", "desc": "Coupure depuis 6h du matin", "heure": "08:15", "confirmations": 5, "statut": "En cours"},
    {"id": 2, "quartier": "Odza", "type": "Eau", "desc": "Pas d'eau depuis hier soir", "heure": "07:40", "confirmations": 3, "statut": "En cours"},
]
prochain_id = 3

QUARTIERS = ["Mokolo", "Biyem-Assi", "Odza", "Mvog-Mbi", "Nlongkak", "Essos", "Ngoa-Ekelle", "Melen", "Emana", "Nkolbisson"]

COORDS = {
    "Mokolo": [3.879, 11.504],
    "Biyem-Assi": [3.831, 11.486],
    "Odza": [3.813, 11.521],
    "Mvog-Mbi": [3.849, 11.516],
    "Nlongkak": [3.876, 11.521],
    "Essos": [3.869, 11.529],
    "Ngoa-Ekelle": [3.859, 11.501],
    "Melen": [3.855, 11.492],
    "Emana": [3.895, 11.512],
    "Nkolbisson": [3.857, 11.461],
}

@app.route("/")
def accueil():
    filtre = request.args.get("filtre", "Tous")
    liste = alertes
    if filtre != "Tous":
        liste = [a for a in alertes if a["type"] == filtre]

    html = "<h1>Yaounde Alerte</h1>"
    html += "<p>Coupures d'eau et d'electricite a Yaounde - en temps reel</p>"
    html += '<a href="/signaler">+ Signaler une coupure</a> | '
    html += '<a href="/statistiques">Statistiques</a> | '
    html += '<a href="/carte">Carte</a> | '
    html += '<a href="/?filtre=Tous">Tous</a> | '
    html += '<a href="/?filtre=Electricite">Electricite</a> | '
    html += '<a href="/?filtre=Eau">Eau</a><hr>'

    if not liste:
        html += "<p>Aucune alerte pour le moment. Tout va bien !</p>"

    for a in reversed(liste):
        emoji = "💡" if a["type"] == "Electricite" else "💧"
        html += "<div style='border:1px solid #ccc; padding:10px; margin:10px;'>"
        html += f"<h3>{emoji} {a['type']} - {a['quartier']}</h3>"
        html += f"<p>{a['desc']}</p>"
        html += f"<p><b>{a['confirmations']} personnes confirment</b> - Signale a {a['heure']}</p>"
        html += f"<p>Statut : {a.get('statut', 'En cours')}</p>"
        html += f"<form action='/confirmer/{a['id']}' method='POST' style='display:inline;'>"
        html += "<button type='submit'>Moi aussi, j'ai la coupure !</button>"
        html += "</form> "
        html += f"<form action='/resolu/{a['id']}' method='POST' style='display:inline;'>"
        html += "<button type='submit'>C'est retabli !</button>"
        html += "</form>"
        html += "</div>"

    return html

@app.route("/confirmer/<int:alerte_id>", methods=["POST"])
def confirmer(alerte_id):
    for a in alertes:
        if a["id"] == alerte_id:
            a["confirmations"] += 1
            break
    return redirect(url_for("accueil"))

@app.route("/resolu/<int:alerte_id>", methods=["POST"])
def resolu(alerte_id):
    for a in alertes:
        if a["id"] == alerte_id:
            a["statut"] = "Retabli"
            break
    return redirect(url_for("accueil"))

@app.route("/signaler", methods=["GET", "POST"])
def signaler():
    global prochain_id
    if request.method == "POST":
        quartier = request.form.get("quartier")
        type_coupure = request.form.get("type")
        desc = request.form.get("desc")
        heure = datetime.now().strftime("%H:%M")

        alertes.append({
            "id": prochain_id,
            "quartier": quartier,
            "type": type_coupure,
            "desc": desc,
            "heure": heure,
            "confirmations": 1,
            "statut": "En cours"
        })
        prochain_id += 1
        return redirect(url_for("accueil"))

    options = "".join([f'<option>{q}</option>' for q in QUARTIERS])
    return f"""
    <h1>Signaler une coupure</h1>
    <form method="POST">
        <label>Quartier :</label><br>
        <select name="quartier">{options}</select><br><br>
        <label>Type :</label><br>
        <select name="type">
            <option>Electricite</option>
            <option>Eau</option>
        </select><br><br>
        <label>Description :</label><br>
        <input type="text" name="desc" placeholder="Ex: Coupure depuis 2h" required style="width:300px"><br><br>
        <button type="submit">Envoyer l'alerte</button>
    </form>
    <br><a href="/">Retour</a>
    """

@app.route("/statistiques")
def statistiques():
    total_alertes = len(alertes)
    total_confirmations = sum(a["confirmations"] for a in alertes)

    par_quartier = Counter(a["quartier"] for a in alertes)
    top_quartiers = par_quartier.most_common(5)

    par_type = Counter(a["type"] for a in alertes)
    nb_eau = par_type.get("Eau", 0)
    nb_elec = par_type.get("Electricite", 0)

    quartier_top = top_quartiers[0][0] if top_quartiers else "Aucun"
    nb_top = top_quartiers[0][1] if top_quartiers else 0

    html = "<h1>Statistiques - Yaounde Alerte</h1>"
    html += '<a href="/">Retour a l\'accueil</a><hr>'

    html += "<h2>Vue d'ensemble</h2>"
    html += f"<p><b>{total_alertes}</b> alertes signalees</p>"
    html += f"<p><b>{total_confirmations}</b> confirmations 'Moi aussi'</p>"
    html += f"<p>Quartier le plus coupe : <b>{quartier_top}</b> avec {nb_top} alertes</p><hr>"

    html += "<h2>Electricite vs Eau</h2>"
    html += f"<p>Electricite : <b>{nb_elec}</b> alertes</p>"
    html += f"<p>Eau : <b>{nb_eau}</b> alertes</p><hr>"

    html += "<h2>Top 5 des quartiers les plus coupes</h2>"
    if not top_quartiers:
        html += "<p>Pas encore de donnees</p>"
    else:
        for i, (quartier, nb) in enumerate(top_quartiers, 1):
            barre = "█" * nb
            html += f"<p>{i}. <b>{quartier}</b> - {nb} coupure(s) {barre}</p>"

    html += "<hr><h2>Toutes les alertes</h2>"
    for a in alertes:
        html += f"<p>{a['quartier']} - {a['type']} - {a['confirmations']} confirmations - {a.get('statut', 'En cours')}</p>"

    return html

@app.route("/carte")
def carte():
    points = []
    for quartier in QUARTIERS:
        lat, lon = COORDS[quartier]
        nb_en_cours = len([a for a in alertes if a["quartier"] == quartier and a.get("statut", "En cours") == "En cours"])
        couleur = "red" if nb_en_cours > 0 else "green"
        if nb_en_cours > 0:
            texte = f"{quartier} - {nb_en_cours} coupure(s) en cours"
        else:
            texte = f"{quartier} - OK, pas de coupure"
        points.append({"quartier": quartier, "lat": lat, "lon": lon, "couleur": couleur, "texte": texte})

    js_points = ""
    for p in points:
        js_points += f"""
        L.circleMarker([{p['lat']}, {p['lon']}], {{color: '{p['couleur']}', fillColor: '{p['couleur']}', fillOpacity: 0.8, radius: 14}}).addTo(map).bindPopup("{p['texte']}");
        """

    return f"""
    <h1>Carte de Yaounde - Coupures</h1>
    <p><span style="color:red;">Rouge = Coupure en cours</span> | <span style="color:green;">Vert = Pas de coupure</span></p>
    <a href="/">Retour a l'accueil</a> | <a href="/signaler">+ Signaler</a> | <a href="/statistiques">Statistiques</a>
    <br><br>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <div id="map" style="height: 600px; width: 100%;"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        var map = L.map('map').setView([3.848, 11.502], 13);
        L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '© OpenStreetMap'
        }}).addTo(map);
        {js_points}
    </script>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)