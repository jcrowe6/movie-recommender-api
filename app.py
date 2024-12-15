from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load your matrix (replace with your actual matrix loading logic)
S_mod = np.load("S_mod.npy")  # Example: NumPy matrix

# Load movie title table
movies = pd.read_csv('movies.dat', sep='::', engine = 'python',
                     encoding="ISO-8859-1", header = None)
movies.columns = ['MovieID', 'Title', 'Genres']
multiple_idx = pd.Series([("|" in movie) for movie in movies['Genres']])
movies.loc[multiple_idx, 'Genres'] = 'Multiple'
movies.set_index('MovieID')

# Load predefined top movies
top20s = [2858, 260, 1196, 1210, 2028, 1198, 593, 2571, 2762, 589, 608, 527, 110, 1270, 318, 858, 480, 1197, 2396, 1617]

# Define a function to compute recommendations
def ICBF(newuser: pd.Series) -> list:
    wmask = ~np.isnan(newuser)
    out = newuser.copy()
    for i in range(len(newuser)):
        if np.isnan(newuser[i]): # Wasn't rated by user
            mask = (~np.isnan(S_mod[i,:])) & wmask
            num = np.nansum(S_mod[i,mask]*newuser[mask])
            den = np.nansum(S_mod[i,mask])
            out[i] = num/den
        else:
            out[i] = np.nan # Don't recommend those already rated
    out = list(map(lambda s : int(s[1:]), out.sort_values(ascending=False)[:10].index))
    if len(out) < 10:
        nmore = 10-len(out)
        topFiltered = list(filter(lambda i : i not in out,top20s))
        out = out + topFiltered[:nmore]
    return out

# Define an API route for recommendations
@app.route('/api/movieapi/recommend', methods=['POST'])
def recommend():
    try:
        # Get input ratings as JSON
        input_data = request.get_json()
        
        # Load Blank user
        fullRatings = pd.read_csv('blankUser.csv', header=0, names=['', 'values'], index_col=0)["values"]

        # populate with provided ratings
        for mid in input_data:
            fullRatings[mid] = input_data[mid]

        # Compute recommendations
        recommendations = ICBF(fullRatings)
        
        # get titles
        titles = list(movies.loc[recommendations]["Title"])

        # Return recommendations as JSON
        response = jsonify({
            "success": True,
            "recs": list(zip(recommendations,titles))
        })
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    
# Define an API route for recommendations
@app.route('/api/movieapi/getInitialMovies', methods=['GET'])
def getInitialMovies():
    try:
        titles = list(movies.loc[top20s]["Title"])
        # Return recommendations as JSON
        response = jsonify({
            "success": True,
            "recs": list(zip(top20s,titles))
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)