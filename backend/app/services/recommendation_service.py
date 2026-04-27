"""
Recommendation Service
======================
Content-based filtering for shoe recommendations.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from app.database.connection import get_pool
from app.services.shoe_service import get_shoe_by_id

async def get_recommendations(shoe_id: int, limit: int = 4) -> list[dict]:
    """
    Get top-N similar shoes using content-based filtering.
    """
    target_shoe = await get_shoe_by_id(shoe_id)
    if not target_shoe:
        return []

    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Fetch all active shoes EXCEPT the target shoe
            await cur.execute("SELECT * FROM shoes WHERE is_active = TRUE AND id != %s", (shoe_id,))
            candidate_shoes = await cur.fetchall()

    if not candidate_shoes:
        return []

    # Prepare data for processing
    df = pd.DataFrame(candidate_shoes)
    
    # Weights for different features
    WEIGHTS = {
        'category': 0.35,
        'brand': 0.20,
        'price': 0.25,
        'description': 0.20
    }

    # 1. Category & Brand Matching
    df['category_match'] = (df['category'] == target_shoe['category']).astype(float)
    df['brand_match'] = (df['brand'] == target_shoe['brand']).astype(float)

    # 2. Price Proximity
    target_price = float(target_shoe['price'])
    if target_price > 0:
        # Avoid division by zero, max difference ratio is 1.0 (100%)
        # Normalization logic: price difference / max(target_price, candidate_price)
        price_diff = abs(df['price'].astype(float) - target_price)
        max_price = df['price'].astype(float).clip(lower=target_price) # avoid zero division
        df['price_score'] = 1.0 - (price_diff / max_price).clip(upper=1.0)
    else:
        df['price_score'] = 0.0

    # 3. Description Similarity (TF-IDF)
    # Combine target and candidates descriptions
    descriptions = [str(target_shoe.get('description', ''))] + df['description'].fillna('').astype(str).tolist()
    
    # Process text using TF-IDF
    tfidf = TfidfVectorizer(stop_words='english', min_df=1) # using english stopwords for general terms, can be expanded
    try:
        tfidf_matrix = tfidf.fit_transform(descriptions)
        # Calculate cosine similarity between target (index 0) and all others
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        df['description_score'] = cosine_sim
    except ValueError:
        # Fallback if TF-IDF fails (e.g. empty descriptions)
        df['description_score'] = 0.0

    # 4. Calculate Final Score
    df['final_score'] = (
        (df['category_match'] * WEIGHTS['category']) +
        (df['brand_match'] * WEIGHTS['brand']) +
        (df['price_score'] * WEIGHTS['price']) +
        (df['description_score'] * WEIGHTS['description'])
    )

    # Sort and get top N
    top_indices = df.nlargest(limit, 'final_score').index
    top_shoes = df.loc[top_indices]

    # Convert back to dict and format
    recommended = []
    for _, row in top_shoes.iterrows():
        shoe_dict = row.to_dict()
        shoe_dict['match_score'] = round(shoe_dict['final_score'] * 100, 1) # Convert to percentage
        recommended.append(shoe_dict)

    return recommended
