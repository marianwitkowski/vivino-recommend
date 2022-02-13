from flask import Flask, flash, request, redirect, render_template
import secrets
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

app = Flask(__name__)
app.secret_key = secrets.token_hex(64)

df_info = pd.read_csv("vivino-info.csv")
df_vivino = pd.read_csv("vivino-out.zip")

def validate_url(url):
    url = url.strip().lower()
    if not 'vivino.com' in url:
        return None
    try:
        wine_id = int(url.split("/")[-1])
        return wine_id
    except:
        return None

@app.route("/", methods=["GET", "POST"])
def upload_form():
    sample : pd.DataFrame = None
    df_result : pd.DataFrame = None
    wine_url = ""
    if request.method == "GET" and (request.args.get("rnd",None) or False):
        ix = df_info.sample(n=1).index[0]
        sample = df_vivino.iloc[[ix]]

    if request.method == "POST" and (request.form.get("wine",None) or False):
        wine_url = request.form.get("wine","")
        wine_id = validate_url(wine_url)
        if wine_id is None:
            flash("Podaj poprawny adres ze strony vivino.com")
        else:
            sample = df_info.query(f" id=={wine_id} ")
            if sample.shape[0]!=1:
                flash(f"Przepraszamy, nie znaleziono tego wina - {wine_url}")
                return redirect(request.url)
            ix = sample.index[0]
            sample = df_vivino.iloc[[ix]]

    if sample is not None:
        df_vivino['distance'] = euclidean_distances(sample, df_vivino).ravel()
        df_result = df_info.loc[df_vivino.sort_values('distance').head(21).index]

    result = []
    if df_result is not None:
        result = df_result.to_dict('records')
    return render_template("form.html", wines=result, wine_url=wine_url)

