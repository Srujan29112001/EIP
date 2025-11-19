"""
Spark Streaming Job for News Processing
Consumes from Kafka news_stream, processes, and writes to databases
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
import os


# Define schema for news messages
news_schema = StructType([
    StructField("type", StringType(), True),
    StructField("title", StringType(), True),
    StructField("content", StringType(), True),
    StructField("source", StringType(), True),
    StructField("url", StringType(), True),
    StructField("category", StringType(), True),
    StructField("sentiment", StringType(), True),
    StructField("published_at", StringType(), True),
    StructField("timestamp", StringType(), True)
])


def create_spark_session():
    """Create Spark session with required configurations"""
    return SparkSession.builder \
        .appName("EIP-NewsProcessing") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .getOrCreate()


def process_news_stream():
    """Main news processing job"""
    spark = create_spark_session()

    # Read from Kafka
    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", "news_stream") \
        .option("startingOffsets", "latest") \
        .load()

    # Parse JSON
    news_df = df.select(
        from_json(col("value").cast("string"), news_schema).alias("news")
    ).select("news.*")

    # Add processing timestamp
    processed_df = news_df.withColumn("processed_at", current_timestamp())

    # Sentiment analysis UDF (placeholder - in production use ML model)
    @udf(StringType())
    def analyze_sentiment(content):
        if content and len(content) > 0:
            # Placeholder logic - use actual NLP model in production
            positive_words = ["good", "great", "excellent", "positive", "growth"]
            negative_words = ["bad", "poor", "negative", "decline", "loss"]

            content_lower = content.lower()
            pos_count = sum(1 for word in positive_words if word in content_lower)
            neg_count = sum(1 for word in negative_words if word in content_lower)

            if pos_count > neg_count:
                return "positive"
            elif neg_count > pos_count:
                return "negative"
            else:
                return "neutral"
        return "neutral"

    # Update sentiment if not provided
    final_df = processed_df.withColumn(
        "sentiment",
        udf(lambda s, c: s if s else analyze_sentiment(c))(col("sentiment"), col("content"))
    )

    # Write to PostgreSQL (batch writes)
    def write_to_postgres(batch_df, batch_id):
        jdbc_url = os.getenv("POSTGRES_URL", "jdbc:postgresql://localhost:5432/eip_db")
        properties = {
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "password"),
            "driver": "org.postgresql.Driver"
        }

        batch_df.write \
            .jdbc(url=jdbc_url, table="news_articles", mode="append", properties=properties)

    # Write stream to PostgreSQL
    query = final_df.writeStream \
        .foreachBatch(write_to_postgres) \
        .outputMode("append") \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    process_news_stream()
