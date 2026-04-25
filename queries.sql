-- ================================================
-- Indian E-Commerce Sentiment Analysis
-- SQL Business Questions
-- ================================================

-- Q1: Which brand has the best overall sentiment?
SELECT brand,
       ROUND(AVG(sentiment_score), 3) AS avg_sentiment,
       COUNT(*) AS total_posts
FROM analyzed_data
GROUP BY brand
ORDER BY avg_sentiment DESC;

-- Q2: Positive vs Negative % per brand
SELECT brand,
       sentiment_label,
       COUNT(*) AS count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*))
             OVER (PARTITION BY brand), 1) AS percentage
FROM analyzed_data
GROUP BY brand, sentiment_label
ORDER BY brand;

-- Q3: YouTube public vs News media sentiment gap
SELECT brand,
       source,
       ROUND(AVG(sentiment_score), 3) AS avg_score,
       COUNT(*) AS total
FROM analyzed_data
GROUP BY brand, source
ORDER BY brand;

-- Q4: Which brand has most negative posts?
SELECT brand,
       COUNT(*) AS negative_count
FROM analyzed_data
WHERE sentiment_label = 'Negative'
GROUP BY brand
ORDER BY negative_count DESC;

-- Q5: Most liked negative posts (real complaints)
SELECT brand, source, text, upvotes,
       ROUND(sentiment_score, 3) AS score
FROM analyzed_data
WHERE sentiment_label = 'Negative'
ORDER BY upvotes DESC
LIMIT 10;

-- Q6: Most liked positive posts
SELECT brand, source, text, upvotes,
       ROUND(sentiment_score, 3) AS score
FROM analyzed_data
WHERE sentiment_label = 'Positive'
ORDER BY upvotes DESC
LIMIT 10;

-- Q7: Brand with highest positive %
SELECT brand,
       ROUND(SUM(CASE WHEN sentiment_label='Positive'
             THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1)
             AS positive_percentage
FROM analyzed_data
GROUP BY brand
ORDER BY positive_percentage DESC;