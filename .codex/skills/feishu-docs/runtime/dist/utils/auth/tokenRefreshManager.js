import { Logger } from '../logger.js';
import { TokenCacheManager } from './tokenCacheManager.js';
import { AuthService } from '../../services/feishuAuthService.js';
/**
 * Token自动刷新管理器
 * 定期检查并自动刷新即将过期的用户token
 */
export class TokenRefreshManager {
    /**
     * 私有构造函数，用于单例模式
     */
    constructor() {
        Object.defineProperty(this, "intervalId", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: null
        });
        Object.defineProperty(this, "checkInterval", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: 5 * 60 * 1000
        }); // 5分钟
        Object.defineProperty(this, "isRunning", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: false
        });
        Logger.info('Token刷新管理器已初始化');
    }
    /**
     * 获取TokenRefreshManager实例
     */
    static getInstance() {
        if (!TokenRefreshManager.instance) {
            TokenRefreshManager.instance = new TokenRefreshManager();
        }
        return TokenRefreshManager.instance;
    }
    /**
     * 启动自动刷新检查
     */
    start() {
        if (this.isRunning) {
            Logger.warn('Token刷新管理器已在运行中');
            return;
        }
        Logger.info(`启动Token自动刷新管理器，检查间隔: ${this.checkInterval / 1000}秒`);
        // 立即执行一次检查
        this.checkAndRefreshTokens();
        // 设置定时器（不阻止进程在 stdio 模式下自然退出）
        this.intervalId = setInterval(() => {
            this.checkAndRefreshTokens();
        }, this.checkInterval);
        this.intervalId.unref();
        this.isRunning = true;
        Logger.info('Token自动刷新管理器已启动');
    }
    /**
     * 停止自动刷新检查
     */
    stop() {
        if (!this.isRunning) {
            Logger.warn('Token刷新管理器未在运行');
            return;
        }
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.isRunning = false;
        Logger.info('Token自动刷新管理器已停止');
    }
    /**
     * 检查并刷新即将过期的token
     */
    async checkAndRefreshTokens() {
        try {
            Logger.debug('开始检查需要刷新的token');
            const tokenCacheManager = TokenCacheManager.getInstance();
            // 获取所有用户token
            const allCacheKeys = this.getAllUserTokenKeys();
            let checkedCount = 0;
            let refreshedCount = 0;
            let failedCount = 0;
            for (const clientKey of allCacheKeys) {
                checkedCount++;
                try {
                    const tokenInfo = tokenCacheManager.getUserTokenInfo(clientKey);
                    if (!tokenInfo) {
                        Logger.debug(`无token信息，跳过: ${clientKey}`);
                        continue;
                    }
                    const now = Math.floor(Date.now() / 1000);
                    const refreshTokenTimeToExpiry = tokenInfo.refresh_token_expires_at
                        ? Math.max(0, tokenInfo.refresh_token_expires_at - now)
                        : 0;
                    const isRefreshTokenExpiringSoon = refreshTokenTimeToExpiry > 0 && refreshTokenTimeToExpiry < 600;
                    // 检查是否需要刷新：refresh_token 即将过期（5分钟内）
                    if (isRefreshTokenExpiringSoon) {
                        Logger.info(`检测到refresh_token即将过期，主动刷新: ${clientKey}`);
                        // 验证是否有刷新所需的必要信息
                        if (!tokenInfo.refresh_token) {
                            Logger.warn(`token没有refresh_token，无法刷新: ${clientKey}`);
                            failedCount++;
                            continue;
                        }
                        if (!tokenInfo.client_id || !tokenInfo.client_secret) {
                            Logger.warn(`token缺少client_id或client_secret，无法刷新: ${clientKey}`);
                            failedCount++;
                            continue;
                        }
                        // 执行刷新，使用AuthService的统一刷新方法
                        try {
                            const authService = new AuthService();
                            await authService.refreshUserToken(clientKey);
                            refreshedCount++;
                            Logger.info(`token刷新成功: ${clientKey}`);
                        }
                        catch (error) {
                            failedCount++;
                            Logger.warn(`token刷新失败: ${clientKey}`, error);
                            // 如果刷新失败是因为refresh_token无效，清除缓存
                            if (error?.response?.data?.code === 99991669 || error?.message?.includes('refresh_token')) {
                                Logger.warn(`refresh_token无效，清除缓存: ${clientKey}`);
                                tokenCacheManager.removeUserToken(clientKey);
                            }
                        }
                    }
                    else {
                        Logger.debug(`refresh_token未到期，无需主动刷新: ${clientKey}`);
                    }
                }
                catch (error) {
                    Logger.error(`检查token时发生错误: ${clientKey}`, error);
                    failedCount++;
                }
            }
            if (refreshedCount > 0 || failedCount > 0) {
                Logger.info(`Token刷新检查完成: 检查${checkedCount}个，刷新${refreshedCount}个，失败${failedCount}个`);
            }
            else {
                Logger.debug(`Token刷新检查完成: 检查${checkedCount}个，无需刷新`);
            }
        }
        catch (error) {
            Logger.error('检查并刷新token时发生错误:', error);
        }
    }
    /**
     * 获取所有用户token的key列表
     */
    getAllUserTokenKeys() {
        try {
            const tokenCacheManager = TokenCacheManager.getInstance();
            return tokenCacheManager.getAllUserTokenKeys();
        }
        catch (error) {
            Logger.error('获取所有用户token key时发生错误:', error);
            return [];
        }
    }
    /**
     * 获取运行状态
     */
    isRunningStatus() {
        return this.isRunning;
    }
}
