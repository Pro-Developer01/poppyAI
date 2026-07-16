import { QueueService } from '../queue/queue.service';
import { JobsService } from '../jobs/jobs.service';
export declare class DocumentsController {
    private readonly queue;
    private readonly jobs;
    constructor(queue: QueueService, jobs: JobsService);
    upload(file: Express.Multer.File): Promise<{
        jobId: string;
        documentId: `${string}-${string}-${string}-${string}-${string}`;
        status: string;
    }>;
    status(id: string): Promise<any>;
}
