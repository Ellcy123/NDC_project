import { FeishuBaseApiService } from '../../../services/feishu/FeishuBaseApiService.js';
export class FeishuCalendarService extends FeishuBaseApiService {
    constructor(authService) {
        super(authService);
    }
}
