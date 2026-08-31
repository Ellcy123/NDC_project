import { Logger } from '../logger.js';
/**
 * 用户认证管理器
 * 管理 sessionId 与 userKey 的映射关系
 */
export class UserAuthManager {
    /**
     * 私有构造函数，用于单例模式
     */
    constructor() {
        Object.defineProperty(this, "sessionToUserKey", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        }); // sessionId -> userKey
        this.sessionToUserKey = new Map();
    }
    /**
     * 获取用户认证管理器实例
     * @returns 用户认证管理器实例
     */
    static getInstance() {
        if (!UserAuthManager.instance) {
            UserAuthManager.instance = new UserAuthManager();
        }
        return UserAuthManager.instance;
    }
    /**
     * 创建用户会话
     * @param sessionId 会话ID
     * @param userKey 用户密钥
     * @returns 是否创建成功
     */
    createSession(sessionId, userKey) {
        if (!sessionId || !userKey) {
            Logger.warn('创建会话失败：sessionId 或 userKey 为空');
            return false;
        }
        this.sessionToUserKey.set(sessionId, userKey);
        Logger.info(`创建用户会话：sessionId=${sessionId}, userKey=${userKey}`);
        return true;
    }
    /**
     * 根据 sessionId 获取 userKey
     * @param sessionId 会话ID
     * @returns 用户密钥，如果未找到则返回 null
     */
    getUserKeyBySessionId(sessionId) {
        if (!sessionId) {
            return null;
        }
        const userKey = this.sessionToUserKey.get(sessionId);
        if (!userKey) {
            Logger.debug(`未找到会话：${sessionId}`);
            return null;
        }
        Logger.debug(`获取用户密钥：sessionId=${sessionId}, userKey=${userKey}`);
        return userKey;
    }
    /**
     * 删除会话
     * @param sessionId 会话ID
     * @returns 是否删除成功
     */
    removeSession(sessionId) {
        if (!sessionId) {
            return false;
        }
        const userKey = this.sessionToUserKey.get(sessionId);
        if (!userKey) {
            Logger.debug(`会话不存在：${sessionId}`);
            return false;
        }
        this.sessionToUserKey.delete(sessionId);
        Logger.info(`删除用户会话：sessionId=${sessionId}, userKey=${userKey}`);
        return true;
    }
    /**
     * 检查会话是否存在
     * @param sessionId 会话ID
     * @returns 会话是否存在
     */
    hasSession(sessionId) {
        return this.sessionToUserKey.has(sessionId);
    }
    /**
     * 获取所有会话统计信息
     * @returns 会话统计信息
     */
    getStats() {
        return {
            totalSessions: this.sessionToUserKey.size
        };
    }
    /**
     * 清空所有会话
     */
    clearAllSessions() {
        const count = this.sessionToUserKey.size;
        this.sessionToUserKey.clear();
        Logger.info(`清空所有会话，删除了 ${count} 个会话`);
    }
}
