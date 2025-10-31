import streamlit as st
import pickle
import requests
import time

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="🎬 Movie Recommender System | Shubham Kumar",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- CSS (Dark Premium Netflix Look) ----------------
st.markdown("""
    <style>
    :root {
        --accent: #ff0000;
        --accent-glow: #ff4d4d;
        --text-light: #eee;
    }

    /* Background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(160deg, #000000, #0d0d0d, #1a1a1a);
        transition: all 0.4s ease;
        color: var(--text-light);
    }

    /* Title */
    h1 {
        text-align: center;
        background: linear-gradient(90deg, #ff0000, #ff6a00, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 15px rgba(255,0,0,0.5);
        font-size: 2.8rem;
        margin-bottom: 5px;
    }

    /* Animated Signature */
    @keyframes glow {
        0% { color: #ff3333; text-shadow: 0 0 10px #ff0000; }
        50% { color: #ff6a00; text-shadow: 0 0 20px #ff6a00; }
        100% { color: #ff3333; text-shadow: 0 0 10px #ff0000; }
    }
    .animated-name {
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        animation: glow 3s infinite;
        margin-bottom: 30px;
    }

    /* Floating Search Bar */
    .search-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
        position: relative;
    }

    div[data-testid="stTextInput"] {
        background: rgba(255,255,255,0.05);
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(255,0,0,0.3);
        transition: all 0.3s ease;
        width: 60% !important;
    }

    div[data-testid="stTextInput"]:hover {
        box-shadow: 0 0 25px rgba(255,0,0,0.6);
        transform: scale(1.02);
    }

    /* Search Button */
    div[data-testid="stButton"] > button {
        background: linear-gradient(90deg, #ff0000, #ff6a00);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s ease;
        border: none;
    }

    div[data-testid="stButton"] > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #ff0000;
    }

    /* Search loader */
    .searching {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .search-icon {
        width: 45px;
        height: 45px;
        border: 3px solid #ff3333;
        border-radius: 50%;
        position: relative;
        animation: spin 2s linear infinite;
    }
    .search-icon::after {
        content: '';
        position: absolute;
        width: 15px;
        height: 3px;
        background: #ff3333;
        top: 27px;
        left: 33px;
        transform: rotate(45deg);
        border-radius: 2px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Movie Reel Animation */
    .reel {
        display: flex;
        justify-content: center;
        margin: 15px 0;
    }
    .reel-wheel {
        width: 50px;
        height: 50px;
        border: 5px dotted #ff3333;
        border-radius: 50%;
        margin: 0 8px;
        animation: roll 3s linear infinite;
    }
    @keyframes roll {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    /* Movie cards */
    .movie-card {
        border-radius: 15px;
        padding: 10px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(8px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .movie-card:hover {
        transform: translateY(-6px) scale(1.03);
        box-shadow: 0 8px 25px rgba(255, 0, 0, 0.4);
    }

    /* Footer */
    .footer {
        text-align: center;
        margin-top: 50px;
        font-size: 15px;
        color: #888;
        position: relative;
    }
    .footer::before {
        content: "";
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 4px;
        border-radius: 5px;
        background: linear-gradient(90deg, #ff0000, #ff6a00, #ffcc00);
        animation: moveLine 3s linear infinite;
    }
    @keyframes moveLine {
        0% { background-position: 0% }
        100% { background-position: 100% }
    }
    </style>
""", unsafe_allow_html=True)

# ---------------- Movie Poster Fetch ----------------
def fetch_poster(movie_id, movie_name=None, session=None):
    try:
        if session is None:
            session = requests.Session()

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=7a3b47545f44fc8b938f4e197877d496&language=en-US"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')

        if not poster_path and movie_name:
            search_url = f"https://api.themoviedb.org/3/search/movie?api_key=7a3b47545f44fc8b938f4e197877d496&query={movie_name}"
            search_data = session.get(search_url, timeout=10).json()
            if search_data.get('results'):
                poster_path = search_data['results'][0].get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Image"

    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750.png?text=Error"

# ---------------- Recommendation Logic ----------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []
    session = requests.Session()

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        movie_name = movies.iloc[i[0]].title
        poster = fetch_poster(movie_id, movie_name, session=session)
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movie_name)
        time.sleep(0.2)

    return recommended_movie_names, recommended_movie_posters

# ---------------- Streamlit UI ----------------
st.title("🎥 Movie Recommender System")
st.markdown('<div class="animated-name">✨ Built by Shubham Kumar ✨</div>', unsafe_allow_html=True)

# Movie Reel Animation
st.markdown('<div class="reel"><div class="reel-wheel"></div><div class="reel-wheel"></div><div class="reel-wheel"></div></div>', unsafe_allow_html=True)

movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values

# Floating Search
st.markdown('<div class="search-container"></div>', unsafe_allow_html=True)
selected_movie = st.selectbox("🎬 Type or select a movie", movie_list, label_visibility="collapsed")

if st.button('Show Recommendation 🎞️'):
    st.markdown('<div class="searching"><div class="search-icon"></div></div>', unsafe_allow_html=True)
    with st.spinner('🍿 Fetching premium recommendations...'):
        names, posters = recommend(selected_movie)
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                st.image(posters[i], caption=names[i])
                st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    🚀 Made with ❤️ by <b>Shubham Kumar</b><br>
    <small>© 2025 Movie Recommender | Streamlit</small>
</div>
""", unsafe_allow_html=True)
