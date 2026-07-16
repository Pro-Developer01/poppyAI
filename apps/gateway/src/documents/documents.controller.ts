import {
    Controller, Post, Get, Param, UploadedFile, UseInterceptors,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { randomUUID } from 'crypto';
import { extname, resolve } from 'path';
import { QueueService } from '../queue/queue.service';
import { JobsService } from '../jobs/jobs.service';

@Controller()
export class DocumentsController {
    constructor(
        private readonly queue: QueueService,
        private readonly jobs: JobsService,
    ) { }

    @Post('documents')
    @UseInterceptors(
        FileInterceptor('file', {
            storage: diskStorage({
                destination: process.env.UPLOAD_DIR || '/data/uploads',
                filename: (_req, file, cb) =>
                    cb(null, `${randomUUID()}${extname(file.originalname)}`),
            }),
        }),
    )
    async upload(@UploadedFile() file: Express.Multer.File) {
        const documentId = randomUUID();
        const jobId = await this.jobs.createJob(documentId, file.originalname);

        // file ka path job message mein — worker shared dir se padhega
        await this.queue.publishIngestion({
            jobId,
            documentId,
            filePath: resolve(file.path),
            filename: file.originalname,
        });

        // turant return — bhaari kaam background mein
        return { jobId, documentId, status: 'processing' };
    }

    @Get('jobs/:id')
    async status(@Param('id') id: string) {
        return this.jobs.getJob(id);
    }
}