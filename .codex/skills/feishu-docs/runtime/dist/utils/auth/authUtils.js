import * as crypto from 'crypto';
import { Config } from '../config.js';
/**
 * 认证工具类
 * 提供认证相关的加密和哈希工具方法
 */
export class AuthUtils {
    /**
     * 生成客户端缓存键
     * @param userKey 用户标识（可选）
     * @returns 生成的客户端键
     */
    static generateClientKey(userKey) {
        const feishuConfig = Config.getInstance().feishu;
        const userPart = userKey ? `:${userKey}` : '';
        let source = '';
        if (feishuConfig.authType === "tenant") {
            source = `${feishuConfig.appId}:${feishuConfig.appSecret}`;
        }
        else {
            source = `${feishuConfig.appId}:${feishuConfig.appSecret}${userPart}`;
        }
        return crypto.createHash('sha256').update(source).digest('hex');
    }
    /**
     * 生成时间戳
     * @returns 当前时间戳（秒）
     */
    static timestamp() {
        return Math.floor(Date.now() / 1000);
    }
    /**
     * 生成时间戳（毫秒）
     * @returns 当前时间戳（毫秒）
     */
    static timestampMs() {
        return Date.now();
    }
    /**
     * 编码state参数
     * @param appId 应用ID
     * @param appSecret 应用密钥
     * @param clientKey 客户端缓存键
     * @param redirectUri 重定向URI（可选）
     * @returns Base64编码的state字符串
     */
    static encodeState(appId, appSecret, clientKey, redirectUri) {
        const stateData = {
            appId,
            appSecret,
            clientKey,
            redirectUri,
            timestamp: this.timestamp()
        };
        return Buffer.from(JSON.stringify(stateData)).toString('base64');
    }
    /**
     * 解码state参数
     * @param encodedState Base64编码的state字符串
     * @returns 解码后的state数据
     */
    static decodeState(encodedState) {
        try {
            const decoded = Buffer.from(encodedState, 'base64').toString('utf-8');
            return JSON.parse(decoded);
        }
        catch (error) {
            return null;
        }
    }
}
