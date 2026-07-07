import streamlit as st
import pickle
import os
import requests
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

OMDB_API_KEY = "b0aa61bc"
FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg"

@st.cache_data
def load_data():
    movies     = pickle.load(open("movies_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()
movies_list = movies["title"].values

def fetch_poster(movie_title):
    try:
        url = f"http://www.omdbapi.com/?t={requests.utils.quote(movie_title)}&apikey={OMDB_API_KEY}"
        r = requests.get(url, timeout=8)
        if r.status_code != 200:
            return FALLBACK
        data = r.json()
        poster = data.get("Poster")
        if not poster or poster == "N/A":
            return FALLBACK
        return poster
    except:
        return FALLBACK

def recommend(movie):
    idx = movies[movies["title"] == movie].index[0]
    distances = sorted(enumerate(similarity[idx]), key=lambda x: x[1], reverse=True)

    top5   = distances[1:6]
    names  = [movies.iloc[i]["title"] for i, _ in top5]
    scores = [round(s * 100, 1) for _, s in top5]

    # Fetch all 5 posters at the same time (fast!)
    with ThreadPoolExecutor(max_workers=5) as ex:
        posters = list(ex.map(fetch_poster, names))

    return names, posters, scores

st.markdown("""
<style>
.card {
    background: linear-gradient(145deg, #1a1a2e, #16213e);
    border: 1px solid #e94560;
    border-radius: 16px;
    padding: 12px;
    text-align: center;
    margin-bottom: 10px;
}
.card img {
    border-radius: 10px;
    width: 100%;
    height: 280px;
    object-fit: cover;
}
.card-title {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    margin: 10px 0 8px 0;
    line-height: 1.4;
}
.badge {
    background: #e94560;
    color: white;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 Movie Recommender System")
st.markdown("##### Find movies similar to your favorites — instantly!")
st.divider()

selected = st.selectbox("🎥 Select a movie", movies_list)

col1, col2, col3 = st.columns([1,1,1])
with col2:
    show = st.button("🎯 Show Recommendations", use_container_width=True)

if show:
    with st.spinner("Fetching recommendations & posters..."):
        names, posters, scores = recommend(selected)

    st.divider()
    st.markdown(f"### Because you liked **{selected}**, try these:")
    st.markdown(" ")

    cols = st.columns(5)
    for col, name, poster, score in zip(cols, names, posters, scores):
        with col:
            st.markdown(f"""
            <div class="card">
                <img src="{poster}" onerror="this.src='{FALLBACK}'" />
                <div class="card-title">{name}</div>
                <span class="badge">⭐ {score}% match</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.success("✅ Recommendations loaded successfully!")