import { AsyncLocalStorage } from 'async_hooks';
/**
 * 用户上下文管理器
 * 使用 AsyncLocalStorage 在异步调用链中传递用户信息
 */
export class UserContextManager {
    constructor() {
        Object.defineProperty(this, "asyncLocalStorage", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.asyncLocalStorage = new AsyncLocalStorage();
    }
    /**
     * 获取单例实例
     */
    static getInstance() {
        if (!UserContextManager.instance) {
            UserContextManager.instance = new UserContextManager();
        }
        return UserContextManager.instance;
    }
    /**
     * 在指定上下文中运行回调函数
     * @param context 用户上下文
     * @param callback 回调函数
     * @returns 回调函数的返回值
     */
    run(context, callback) {
        return this.asyncLocalStorage.run(context, callback);
    }
    /**
     * 获取当前上下文中的用户密钥
     * @returns 用户密钥，如果不存在则返回空字符串
     */
    getUserKey() {
        const context = this.asyncLocalStorage.getStore();
        return context?.userKey || '';
    }
    /**
     * 获取当前上下文中的基础URL
     * @returns 基础URL，如果不存在则返回空字符串
     */
    getBaseUrl() {
        const context = this.asyncLocalStorage.getStore();
        return context?.baseUrl || '';
    }
    /**
     * 获取当前完整的用户上下文
     * @returns 用户上下文，如果不存在则返回 undefined
     */
    getContext() {
        return this.asyncLocalStorage.getStore();
    }
    /**
     * 检查是否存在用户上下文
     * @returns 如果存在用户上下文则返回 true
     */
    hasContext() {
        return this.asyncLocalStorage.getStore() !== undefined;
    }
}
/**
 * 获取协议
 */
function getProtocol(req) {
    if (req.secure || req.get('X-Forwarded-Proto') === 'https') {
        return 'https';
    }
    return 'http';
}
/**
 * 获取基础URL
 */
export function getBaseUrl(req) {
    const protocol = getProtocol(req);
    const host = req.get('X-Forwarded-Host') || req.get('host');
    return `${protocol}://${host}`;
}
