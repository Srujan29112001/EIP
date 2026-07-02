"""
Spark Batch Job for Market Analytics
Processes historical market data and generates analytics
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, count, window, lag, expr
from pyspark.sql.window import Window
import os


def create_spark_session():
    """Create Spark session"""
    return SparkSession.builder \
        .appName("EIP-MarketAnalytics") \
        .getOrCreate()


def calculate_market_metrics(spark, data_path):
    """
    Calculate market metrics from historical data

    Args:
        spark: Spark session
        data_path: Path to market data (Parquet/CSV)
    """
    # Read market data
    market_df = spark.read.parquet(data_path)

    # Calculate daily metrics per symbol
    daily_metrics = market_df.groupBy("symbol", "date") \
        .agg(
            avg("price").alias("avg_price"),
            sum("volume").alias("total_volume"),
            count("*").alias("trade_count")
        )

    # Calculate moving averages
    window_spec = Window.partitionBy("symbol").orderBy("date").rowsBetween(-6, 0)

    moving_avg_df = daily_metrics.withColumn(
        "ma_7day",
        avg("avg_price").over(window_spec)
    )

    # Calculate price changes
    window_lag = Window.partitionBy("symbol").orderBy("date")

    price_change_df = moving_avg_df.withColumn(
        "prev_price",
        lag("avg_price").over(window_lag)
    ).withColumn(
        "price_change_pct",
        ((col("avg_price") - col("prev_price")) / col("prev_price")) * 100
    )

    return price_change_df


def identify_trending_stocks(spark, metrics_df):
    """
    Identify trending stocks based on metrics

    Args:
        spark: Spark session
        metrics_df: DataFrame with market metrics
    """
    # Find stocks with consistent growth
    trending_df = metrics_df.filter(
        (col("price_change_pct") > 5) &
        (col("total_volume") > 100000)
    ).select(
        "symbol",
        "date",
        "avg_price",
        "price_change_pct",
        "total_volume"
    ).orderBy(col("price_change_pct").desc())

    return trending_df


def save_analytics(df, table_name):
    """Save analytics to PostgreSQL"""
    jdbc_url = os.getenv("POSTGRES_URL", "jdbc:postgresql://localhost:5432/eip_db")
    properties = {
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "driver": "org.postgresql.Driver"
    }

    df.write \
        .jdbc(url=jdbc_url, table=table_name, mode="overwrite", properties=properties)


def main():
    """Main analytics job"""
    spark = create_spark_session()

    # Get data path from environment
    data_path = os.getenv("MARKET_DATA_PATH", "/data/market/")

    # Calculate metrics
    metrics_df = calculate_market_metrics(spark, data_path)

    # Identify trending stocks
    trending_df = identify_trending_stocks(spark, metrics_df)

    # Save results
    save_analytics(metrics_df, "market_metrics")
    save_analytics(trending_df, "trending_stocks")

    print(f"Analytics completed. Processed {metrics_df.count()} records.")

    spark.stop()


if __name__ == "__main__":
    main()
