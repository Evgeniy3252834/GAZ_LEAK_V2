import sqlite3
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import logging

from src.domain.entities import LeakDetectionResult, BatchJob, ProcessingStatus
from src.domain.interfaces import RepositoryInterface
from config.config import config

logger = logging.getLogger(__name__)

class SQLiteRepository(RepositoryInterface):
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.get_database_url().replace('sqlite:///', '')
        if not self.db_path:
            self.db_path = config.base_dir / "gas_leak.db"
        
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица для результатов детекции
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id TEXT PRIMARY KEY,
                frame_id TEXT,
                timestamp TEXT,
                leak_probability REAL,
                is_leak INTEGER,
                confidence REAL,
                video_path TEXT,
                created_at TEXT
            )
        ''')
        
        # Таблица для батчевых задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batch_jobs (
                job_id TEXT PRIMARY KEY,
                video_paths TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_detection(self, detection: LeakDetectionResult) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        detection_id = f"det_{detection.frame_id}_{datetime.now().timestamp()}"
        cursor.execute('''
            INSERT INTO detections (id, frame_id, timestamp, leak_probability, is_leak, confidence, video_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            detection_id,
            detection.frame_id,
            detection.timestamp.isoformat(),
            detection.leak_probability,
            1 if detection.is_leak else 0,
            detection.confidence,
            detection.video_path,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return detection_id
    
    def save_batch_job(self, job: BatchJob) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO batch_jobs (job_id, video_paths, status, created_at, updated_at, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job.job_id,
            json.dumps(job.video_paths),
            job.status.value,
            job.created_at.isoformat(),
            job.updated_at.isoformat(),
            job.error_message
        ))
        
        conn.commit()
        conn.close()
        return job.job_id
    
    def get_pending_jobs(self) -> List[BatchJob]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM batch_jobs WHERE status = "processing"')
        rows = cursor.fetchall()
        conn.close()
        
        # Преобразуем rows в BatchJob объекты
        jobs = []
        for row in rows:
            job = BatchJob(
                job_id=row[0],
                video_paths=json.loads(row[1]),
                status=ProcessingStatus(row[2]),
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
                error_message=row[5]
            )
            jobs.append(job)
        
        return jobs
    
    def update_job_status(self, job_id: str, status: str, results: List = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE batch_jobs 
            SET status = ?, updated_at = ?
            WHERE job_id = ?
        ''', (status, datetime.now().isoformat(), job_id))
        
        conn.commit()
        conn.close()
