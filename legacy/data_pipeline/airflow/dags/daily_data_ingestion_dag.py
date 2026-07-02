"""
Airflow DAG for Daily Data Ingestion
Fetches news, market data, and policy updates on a daily schedule
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import requests
import os


# Default DAG arguments
default_args = {
    'owner': 'eip_platform',
    'depends_on_past': False,
    'email': ['alerts@eip-platform.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


# Create DAG
dag = DAG(
    'daily_data_ingestion',
    default_args=default_args,
    description='Daily ingestion of news, market, and policy data',
    schedule_interval='0 2 * * *',  # Run at 2 AM every day
    start_date=days_ago(1),
    catchup=False,
    tags=['data_ingestion', 'daily'],
)


def fetch_news_data(**context):
    """
    Fetch news from external APIs

    In production, this would call:
    - NewsAPI
    - Google News API
    - RSS feeds
    """
    from data_pipeline.kafka.producers import create_news_producer

    # Example: Fetch from NewsAPI
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("NEWS_API_KEY not set, using mock data")
        return

    url = f"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey={api_key}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Publish to Kafka
        producer = create_news_producer()
        for article in data.get('articles', [])[:20]:  # Limit to 20 articles
            producer.publish_news(
                title=article.get('title', ''),
                content=article.get('description', ''),
                source=article.get('source', {}).get('name', 'Unknown'),
                url=article.get('url', ''),
                category='business'
            )
        producer.close()

        print(f"Published {len(data.get('articles', []))} news articles")

    except Exception as e:
        print(f"Error fetching news: {e}")
        raise


def fetch_market_data(**context):
    """
    Fetch market data from external APIs

    In production, this would call:
    - Alpha Vantage
    - Yahoo Finance
    - NSE/BSE APIs
    """
    from data_pipeline.kafka.producers import create_market_producer

    # Example: Fetch from Alpha Vantage
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("ALPHA_VANTAGE_API_KEY not set, using mock data")
        return

    symbols = ['INFY', 'TCS', 'RELIANCE']  # Indian stocks
    producer = create_market_producer()

    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            quote = data.get('Global Quote', {})
            if quote:
                producer.publish_stock_price(
                    symbol=symbol,
                    price=float(quote.get('05. price', 0)),
                    volume=int(quote.get('06. volume', 0)),
                    change_percent=float(quote.get('10. change percent', '0').replace('%', ''))
                )

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    producer.close()
    print(f"Published market data for {len(symbols)} symbols")


def fetch_policy_updates(**context):
    """
    Fetch policy updates from government websites

    In production, this would:
    - Scrape government websites
    - Monitor RSS feeds
    - Use APIs where available
    """
    from data_pipeline.kafka.producers import create_policy_producer

    # This is a placeholder - actual implementation would scrape websites
    print("Policy fetching would happen here")

    # Example: Mock policy update
    producer = create_policy_producer()
    producer.publish_policy_update(
        policy_id="POL-2024-001",
        title="Startup India Initiative Update",
        description="New tax benefits for recognized startups",
        category="taxation",
        effective_date="2024-04-01",
        impact_level="high",
        affected_sectors=["technology", "manufacturing"]
    )
    producer.close()


def validate_ingested_data(**context):
    """Validate that data was ingested successfully"""
    # Check Kafka topics, database records, etc.
    print("Data validation would happen here")
    # In production, query databases to verify record counts
    return True


# Define tasks
fetch_news_task = PythonOperator(
    task_id='fetch_news_data',
    python_callable=fetch_news_data,
    dag=dag,
)

fetch_market_task = PythonOperator(
    task_id='fetch_market_data',
    python_callable=fetch_market_data,
    dag=dag,
)

fetch_policy_task = PythonOperator(
    task_id='fetch_policy_updates',
    python_callable=fetch_policy_updates,
    dag=dag,
)

# Spark job to process news
process_news_task = SparkSubmitOperator(
    task_id='process_news_stream',
    application='/opt/eip/data_pipeline/spark/news_processing_job.py',
    conn_id='spark_default',
    total_executor_cores=2,
    executor_cores=1,
    executor_memory='2g',
    driver_memory='1g',
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_ingested_data,
    dag=dag,
)

# Set task dependencies
[fetch_news_task, fetch_market_task, fetch_policy_task] >> validate_task
