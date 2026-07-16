import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import * as amqp from 'amqplib';

@Injectable()
export class QueueService implements OnModuleInit, OnModuleDestroy {
    private conn!: amqp.ChannelModel;
    private channel!: amqp.Channel;
    private readonly queue = 'ingestion';

    async onModuleInit() {
        this.conn = await amqp.connect(process.env.RABBITMQ_URL!);
        this.channel = await this.conn.createChannel();
        await this.channel.assertQueue(this.queue, { durable: true });
    }

    async publishIngestion(job: Record<string, unknown>) {
        this.channel.sendToQueue(
            this.queue,
            Buffer.from(JSON.stringify(job)),
            { persistent: true },   // message disk pe likhega -> broker restart-safe
        );
    }

    async onModuleDestroy() {
        await this.channel?.close();
        await this.conn?.close();
    }
}
