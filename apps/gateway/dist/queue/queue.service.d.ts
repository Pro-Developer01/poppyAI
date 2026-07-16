import { OnModuleInit, OnModuleDestroy } from '@nestjs/common';
export declare class QueueService implements OnModuleInit, OnModuleDestroy {
    private conn;
    private channel;
    private readonly queue;
    onModuleInit(): Promise<void>;
    publishIngestion(job: Record<string, unknown>): Promise<void>;
    onModuleDestroy(): Promise<void>;
}
