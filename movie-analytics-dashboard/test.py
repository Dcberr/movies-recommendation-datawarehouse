# test_pipeline.py

from services.ai.pipeline.recommender import recommend

results = recommend("phim hài hành động cho trẻ em")

for r in results:
    print(r)