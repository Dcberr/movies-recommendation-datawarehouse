# data/queries.py

# 🔥 Top movies theo weighted rating
TOP_MOVIES = """
SELECT TOP 10
    m.movie_id,
    m.title,
    m.year,
    f.avg_rating,
    f.num_votes,
    f.weighted_rating
FROM fact_movie_stats f
JOIN dim_movie m ON f.movie_id = m.movie_id
ORDER BY f.weighted_rating DESC
"""

# 🎭 Genre distribution
GENRE_DISTRIBUTION = """
SELECT
    g.genre_name,
    COUNT(*) AS total_movies
FROM fact_movie_genre mg
JOIN dim_genre g ON mg.genre_id = g.genre_id
GROUP BY g.genre_name
ORDER BY total_movies DESC
"""

# 📊 Rating distribution
RATING_DISTRIBUTION = """
SELECT avg_rating
FROM fact_movie_stats
"""

# 🎯 Votes vs rating
VOTES_VS_RATING = """
SELECT
    avg_rating,
    num_votes
FROM fact_movie_stats
"""

# 📈 Trend theo năm
YEARLY_TREND = """
SELECT
    m.year,
    AVG(f.weighted_rating) AS avg_weighted_rating
FROM fact_movie_stats f
JOIN dim_movie m ON f.movie_id = m.movie_id
WHERE m.year IS NOT NULL
GROUP BY m.year
ORDER BY m.year
"""

# 📋 Full dataset (để filter phía app)
MOVIE_FULL = """
SELECT
    m.movie_id,
    m.title,
    m.year,
    f.avg_rating,
    f.num_votes,
    f.weighted_rating
FROM fact_movie_stats f
JOIN dim_movie m ON f.movie_id = m.movie_id
"""