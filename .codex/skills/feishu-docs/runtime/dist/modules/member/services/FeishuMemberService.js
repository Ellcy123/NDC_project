import { FeishuBaseApiService } from '../../../services/feishu/FeishuBaseApiService.js';
import { Logger } from '../../../utils/logger.js';
const PAGE_SIZE = 200;
/**
 * 飞书成员搜索 API 服务
 * 封装飞书搜索用户接口（/search/v1/user）、批量获取用户（/contact/v3/users/batch）
 */
export class FeishuMemberService extends FeishuBaseApiService {
    constructor(authService) {
        super(authService);
    }
    /**
     * 通过用户名关键词搜索用户
     * 返回用户头像、用户名、部门、open_id、user_id 等
     * @param query 搜索关键词
     * @param pageToken 分页 token
     */
    async searchUsers(query, pageToken) {
        Logger.info(`搜索用户，关键词: ${query}`);
        const params = {
            query,
            page_size: PAGE_SIZE,
        };
        if (pageToken)
            params.page_token = pageToken;
        return this.get('/search/v1/user', params);
    }
    /**
     * 批量获取用户信息（通讯录）
     * GET /contact/v3/users/batch，返回用户 ID、名称、邮箱、手机、状态、部门等基本信息。
     * 权限：contact:contact.base:readonly。单次最多 50 个 user_id。
     */
    async batchGetUsers(userIds, userIdType = 'open_id') {
        Logger.info(`批量获取用户，数量: ${userIds.length}, user_id_type: ${userIdType}`);
        const qs = new URLSearchParams();
        userIds.forEach((id) => qs.append('user_ids', id));
        qs.set('user_id_type', userIdType);
        const res = await this.get(`/contact/v3/users/batch?${qs.toString()}`, {});
        return res ?? { items: [] };
    }
}
