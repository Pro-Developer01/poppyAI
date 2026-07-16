"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.JobsService = void 0;
const common_1 = require("@nestjs/common");
const pg_1 = require("pg");
let JobsService = class JobsService {
    pool = new pg_1.Pool({ connectionString: process.env.DATABASE_URL });
    async createJob(documentId, filename) {
        const res = await this.pool.query(`INSERT INTO jobs (id, document_id, filename, status, created_at)
       VALUES (gen_random_uuid(), $1, $2, 'processing', now())
       RETURNING id`, [documentId, filename]);
        return res.rows[0].id;
    }
    async getJob(id) {
        const res = await this.pool.query('SELECT * FROM jobs WHERE id = $1', [id]);
        return res.rows[0] ?? null;
    }
};
exports.JobsService = JobsService;
exports.JobsService = JobsService = __decorate([
    (0, common_1.Injectable)()
], JobsService);
//# sourceMappingURL=jobs.service.js.map