"""
Airflow DAG for Weekly Model Retraining
Retrains ML models with latest data and deploys if performance improves
"""
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago
from datetime import timedelta


default_args = {
    'owner': 'eip_platform',
    'depends_on_past': False,
    'email': ['alerts@eip-platform.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
}


dag = DAG(
    'weekly_model_retraining',
    default_args=default_args,
    description='Weekly ML model retraining and deployment',
    schedule_interval='0 2 * * 0',  # Run at 2 AM every Sunday
    start_date=days_ago(1),
    catchup=False,
    tags=['ml', 'training', 'weekly'],
)


def fetch_training_data(**context):
    """Fetch latest training data from databases"""
    print("Fetching training data from PostgreSQL and vector stores...")
    # In production, query databases and create training datasets
    context['task_instance'].xcom_push(key='training_data_path', value='/data/training/dataset.parquet')
    return True


def preprocess_data(**context):
    """Preprocess training data"""
    training_data_path = context['task_instance'].xcom_pull(task_ids='fetch_training_data', key='training_data_path')
    print(f"Preprocessing data from {training_data_path}")

    # In production:
    # - Clean data
    # - Feature engineering
    # - Train/validation split

    context['task_instance'].xcom_push(key='preprocessed_data_path', value='/data/training/preprocessed.parquet')
    return True


def train_sentiment_model(**context):
    """Train sentiment analysis model"""
    data_path = context['task_instance'].xcom_pull(task_ids='preprocess_data', key='preprocessed_data_path')
    print(f"Training sentiment model with data from {data_path}")

    # In production:
    # - Load data
    # - Train transformer model
    # - Log with MLflow

    # Mock metrics
    accuracy = 0.92
    context['task_instance'].xcom_push(key='sentiment_model_accuracy', value=accuracy)
    context['task_instance'].xcom_push(key='sentiment_model_path', value='/models/sentiment/v2')

    return True


def evaluate_models(**context):
    """Evaluate new models against current production models"""
    new_accuracy = context['task_instance'].xcom_pull(task_ids='train_sentiment_model', key='sentiment_model_accuracy')
    current_accuracy = 0.88  # Would fetch from production

    print(f"New model accuracy: {new_accuracy}, Current: {current_accuracy}")

    # Compare performance
    if new_accuracy > current_accuracy:
        print("New model performs better - will deploy")
        return 'register_and_deploy'
    else:
        print("New model doesn't improve performance - skipping deployment")
        return 'skip_deployment'


def register_and_deploy(**context):
    """Register model in MLflow and deploy to production"""
    model_path = context['task_instance'].xcom_pull(task_ids='train_sentiment_model', key='sentiment_model_path')
    print(f"Registering model from {model_path} in MLflow")

    # In production:
    # - Register model in MLflow
    # - Transition to "Production" stage
    # - Update model serving endpoints

    print("Model successfully deployed to production")
    return True


def skip_deployment(**context):
    """Skip deployment if model doesn't improve"""
    print("Skipping deployment - model performance did not improve")
    return True


def send_training_report(**context):
    """Send training report via email"""
    # Get metrics from XCom
    new_accuracy = context['task_instance'].xcom_pull(task_ids='train_sentiment_model', key='sentiment_model_accuracy')

    print(f"Sending training report...")
    print(f"New model accuracy: {new_accuracy}")

    # In production, send actual email with detailed metrics
    return True


# Define tasks
fetch_data_task = PythonOperator(
    task_id='fetch_training_data',
    python_callable=fetch_training_data,
    dag=dag,
)

preprocess_task = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    dag=dag,
)

train_task = PythonOperator(
    task_id='train_sentiment_model',
    python_callable=train_sentiment_model,
    dag=dag,
)

evaluate_task = BranchPythonOperator(
    task_id='evaluate_models',
    python_callable=evaluate_models,
    dag=dag,
)

deploy_task = PythonOperator(
    task_id='register_and_deploy',
    python_callable=register_and_deploy,
    dag=dag,
)

skip_task = PythonOperator(
    task_id='skip_deployment',
    python_callable=skip_deployment,
    dag=dag,
)

report_task = PythonOperator(
    task_id='send_training_report',
    python_callable=send_training_report,
    trigger_rule='none_failed',  # Run even if deployment was skipped
    dag=dag,
)

# Set task dependencies
fetch_data_task >> preprocess_task >> train_task >> evaluate_task
evaluate_task >> [deploy_task, skip_task]
[deploy_task, skip_task] >> report_task
