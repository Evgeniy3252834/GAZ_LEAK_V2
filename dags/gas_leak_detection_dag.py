from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
import logging

default_args = {
    'owner': 'gas-leak-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['alerts@example.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'gas_leak_detection_batch',
    default_args=default_args,
    description='Batch processing for gas leak detection from drone videos',
    schedule_interval='*/15 * * * *',
    catchup=False,
    max_active_runs=1,  # Идемпотентность
    tags=['gas-leak', 'computer-vision'],
)

def check_for_new_videos(**context):
    """Проверка наличия новых видео для обработки"""
    from pathlib import Path
    
    input_dir = Path('/opt/airflow/data/input_videos')
    processed_dir = Path('/opt/airflow/data/processed')
    processed_dir.mkdir(exist_ok=True)
    
    videos = []
    for ext in ['*.mp4', '*.avi', '*.mov']:
        videos.extend(input_dir.glob(ext))
    
    new_videos = []
    for video in videos:
        processed_flag = processed_dir / f"{video.name}.done"
        if not processed_flag.exists():
            new_videos.append(str(video))
    
    context['ti'].xcom_push(key='new_videos_count', value=len(new_videos))
    return len(new_videos)

def backfill_processed_videos(**context):
    """Бэкфилл для уже обработанных видео (восстановление состояния)"""
    from pathlib import Path
    import json
    from datetime import datetime
    
    processed_dir = Path('/opt/airflow/data/processed')
    results_file = processed_dir / 'backfill_manifest.json'
    
    # Создаем манифест обработанных видео
    processed_videos = []
    for done_file in processed_dir.glob('*.done'):
        video_name = done_file.stem
        processed_videos.append({
            'video_name': video_name,
            'processed_at': datetime.fromtimestamp(done_file.stat().st_mtime).isoformat(),
            'status': 'completed'
        })
    
    # Сохраняем манифест
    with open(results_file, 'w') as f:
        json.dump(processed_videos, f, indent=2)
    
    logging.info(f"Backfill completed. Found {len(processed_videos)} processed videos")
    return len(processed_videos)

# Task 1: Проверка новых видео
check_videos = PythonOperator(
    task_id='check_for_new_videos',
    python_callable=check_for_new_videos,
    dag=dag,
)

# Task 2: Бэкфилл (восстановление состояния)
backfill_task = PythonOperator(
    task_id='backfill_processed_videos',
    python_callable=backfill_processed_videos,
    dag=dag,
)

# Task 3: Docker оператор для обработки видео
process_videos = DockerOperator(
    task_id='process_videos_batch',
    image='gas-leak-detector:latest',
    container_name='gas-leak-batch-{{ ds_nodash }}',
    command='python -m src.cli.batch_process --input-dir /data/input_videos --output-dir /data/results',
    environment={
        'ENVIRONMENT': 'production',
        'LOG_LEVEL': 'INFO',
        'USE_GPU': 'false',
    },
    volumes=['/opt/airflow/data:/data'],
    network_mode='bridge',
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    dag=dag,
)

# Task 4: Очистка старых видео (опционально)
cleanup_old_videos = BashOperator(
    task_id='cleanup_old_videos',
    bash_command='find /opt/airflow/data/input_videos -type f -name "*.mp4" -mtime +7 -delete',
    dag=dag,
)

# Определяем зависимости
check_videos >> backfill_task >> process_videos >> cleanup_old_videos
