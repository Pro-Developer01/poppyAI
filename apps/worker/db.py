# import psycopg2
# from .config import settings

# def update_job(job_id: str, status: str, error: str | None = None):
#     try:
#         conn = psycopg2.connect(settings.database_url)
#         cur = conn.cursor()
#         cur.execute(
#             "UPDATE jobs SET status=%s, error=%s, updated_at=now() WHERE id=%s",
#             (status, error, job_id),
#         )
#         conn.commit()
#     except Exception as e:
#         raise e
#     finally:
#         if 'cur' in locals():
#             cur.close()
#         if 'conn' in locals():
#             conn.close()


import psycopg2
from .config import settings

def update_job(job_id: str, status: str, error: str | None = None):
    with psycopg2.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE jobs SET status=%s, error=%s, updated_at=now() WHERE id=%s",
                (status, error, job_id),
            )
        conn.commit()