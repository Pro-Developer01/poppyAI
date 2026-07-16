import { Injectable } from '@nestjs/common';
import { Pool } from 'pg';

@Injectable()
export class JobsService {
    private pool = new Pool({ connectionString: process.env.DATABASE_URL });

    async createJob(documentId: string, filename: string): Promise<string> {
        const res = await this.pool.query(
            `INSERT INTO jobs (id, document_id, filename, status, created_at)
       VALUES (gen_random_uuid(), $1, $2, 'processing', now())
       RETURNING id`,
            [documentId, filename],
        );
        return res.rows[0].id;
    }

    async getJob(id: string) {
        const res = await this.pool.query('SELECT * FROM jobs WHERE id = $1', [id]);
        return res.rows[0] ?? null;
    }
}
