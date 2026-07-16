import { Module } from '@nestjs/common';
import { QueueService } from './queue/queue.service';
import { JobsService } from './jobs/jobs.service';
import { DocumentsController } from './documents/documents.controller';
import { QueryController } from './query/query.controller';

@Module({
  controllers: [DocumentsController, QueryController],
  providers: [QueueService, JobsService],
})
export class AppModule { }