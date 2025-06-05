import http.server
import socketserver
import urllib.parse
import webbrowser
import json
import os
import requests

PORT = 8000
HISTORIQUE_FILE = "historique.json"
CORPUS_FILE = "corpus.txt"
MOT_DE_PASSE = "APZOEIruty3164977/*"

def resume_texte(txt, max_len=500):
    return txt[:max_len] + "..." if len(txt) > max_len else txt

def chercher_wikipedia(query):
    url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            return data.get("extract", "Rien trouvé.")
        return "Erreur Wikipedia"
    except:
        return "Erreur de connexion"

def charger_historique():
    if not os.path.exists(HISTORIQUE_FILE):
        return []
    with open(HISTORIQUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def sauvegarder_historique(h):
    with open(HISTORIQUE_FILE, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=2)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/?q="):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            question = params.get("q", [""])[0]
            if not question:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Aucune question reçue.")
                return
            reponse = chercher_wikipedia(question)
            historique = charger_historique()
            historique.append({"question": question, "reponse": reponse})
            sauvegarder_historique(historique)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(reponse.encode("utf-8"))

        elif self.path.startswith("/historique"):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            password = params.get("mdp", [""])[0]
            self.send_response(200)
            self.end_headers()
            if password != MOT_DE_PASSE:
                self.wfile.write(b"Mot de passe incorrect.")
                return
            historique = charger_historique()
            html = "<h2>Historique</h2><ul>"
            for h in historique:
                html += f"<li><b>{h['question']}</b><br>{resume_texte(h['reponse'])}</li>"
            html += "</ul>"
            self.wfile.write(html.encode("utf-8"))

        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"""
                <html><head><title>IA Web</title></head><body>
                <h2>Pose ta question :</h2>
                <form action="/" method="get">
                    <input name="q" style="width:300px;" />
                    <button type="submit">Envoyer</button>
                </form>
                <br>
                <h3>Voir l'historique</h3>
                <form action="/historique" method="get">
                    Mot de passe : <input name="mdp" type="password" />
                    <button type="submit">Voir</button>
                </form>
                </body></html>
            """)

# Lancement automatique
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serveur actif sur http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    httpd.serve_forever()
