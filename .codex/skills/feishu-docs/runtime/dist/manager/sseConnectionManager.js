import { Logger } from '../utils/logger.js';
/**
 * SSE连接管理器 - 负责管理所有的SSE长连接和心跳机制
 */
export class SSEConnectionManager {
    constructor() {
        Object.defineProperty(this, "transports", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: {}
        });
        Object.defineProperty(this, "connections", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: new Map()
        });
        Object.defineProperty(this, "keepAliveIntervalId", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: null
        });
        Object.defineProperty(this, "KEEP_ALIVE_INTERVAL_MS", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: 1000 * 25
        }); // 25秒心跳间隔
        this.startGlobalKeepAlive();
    }
    /**
     * 启动全局心跳管理
     */
    startGlobalKeepAlive() {
        if (this.keepAliveIntervalId) {
            clearInterval(this.keepAliveIntervalId);
        }
        this.keepAliveIntervalId = setInterval(() => {
            for (const [sessionId, connection] of this.connections.entries()) {
                if (!connection.res.writableEnded) {
                    connection.res.write(': keepalive\n\n');
                }
                else {
                    // 移除已关闭的连接
                    this.removeConnection(sessionId);
                }
            }
        }, this.KEEP_ALIVE_INTERVAL_MS);
        // 不阻止进程在无活跃连接时自然退出（stdio 模式）
        this.keepAliveIntervalId.unref();
    }
    /**
     * 添加新的SSE连接
     */
    addConnection(sessionId, transport, req, res) {
        this.transports[sessionId] = transport;
        this.connections.set(sessionId, { res });
        Logger.info(`[SSE Connection] Client connected: ${sessionId}`);
        req.on('close', () => {
            this.removeConnection(sessionId);
        });
    }
    /**
     * 移除SSE连接
     */
    removeConnection(sessionId) {
        const transport = this.transports[sessionId];
        if (transport) {
            try {
                transport.close();
                Logger.info(`[SSE Connection] Transport closed for: ${sessionId}`);
            }
            catch (error) {
                Logger.error(`[SSE Connection] Error closing transport for: ${sessionId}`, error);
            }
        }
        delete this.transports[sessionId];
        this.connections.delete(sessionId);
        Logger.info(`[SSE Connection] Client disconnected: ${sessionId}`);
    }
    /**
     * 获取指定sessionId的传输实例
     */
    getTransport(sessionId) {
        Logger.debug(`[SSE Connection] Getting transport for sessionId: ${sessionId}`);
        return this.transports[sessionId];
    }
    /**
     * 关闭连接管理器
     */
    shutdown() {
        if (this.keepAliveIntervalId) {
            clearInterval(this.keepAliveIntervalId);
            this.keepAliveIntervalId = null;
        }
        // 关闭所有连接
        Logger.info(`[SSE Connection] Shutting down all connections (${this.connections.size} active)`);
        for (const sessionId of this.connections.keys()) {
            this.removeConnection(sessionId);
        }
        Logger.info(`[SSE Connection] All connections closed`);
    }
}
