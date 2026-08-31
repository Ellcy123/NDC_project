import { FeishuBaseApiService } from '../../../services/feishu/FeishuBaseApiService.js';
import { Logger } from '../../../utils/logger.js';
/**
 * 飞书任务 API 服务
 * 封装飞书任务 v2 API（/task/v2/...）
 */
export class FeishuTaskService extends FeishuBaseApiService {
    constructor(authService) {
        super(authService);
    }
    async createTask(params) {
        Logger.info(`创建任务: ${params.summary}`);
        const body = { summary: params.summary };
        if (params.description !== undefined)
            body.description = params.description;
        if (params.due !== undefined)
            body.due = params.due;
        if (params.completed_at !== undefined)
            body.completed_at = params.completed_at;
        if (params.members?.length)
            body.members = params.members;
        if (params.repeat_rule !== undefined)
            body.repeat_rule = params.repeat_rule;
        if (params.start !== undefined)
            body.start = params.start;
        if (params.mode !== undefined)
            body.mode = params.mode;
        if (params.is_milestone !== undefined)
            body.is_milestone = params.is_milestone;
        return this.post('/task/v2/tasks', body);
    }
    /**
     * 在父任务下创建子任务。请求体与创建任务一致。
     * POST /task/v2/tasks/:task_guid/subtasks
     */
    async createSubtask(parentTaskGuid, params) {
        Logger.info(`创建子任务: ${params.summary}, parent: ${parentTaskGuid}`);
        const body = { summary: params.summary };
        if (params.description !== undefined)
            body.description = params.description;
        if (params.due !== undefined)
            body.due = params.due;
        if (params.completed_at !== undefined)
            body.completed_at = params.completed_at;
        if (params.members?.length)
            body.members = params.members;
        if (params.repeat_rule !== undefined)
            body.repeat_rule = params.repeat_rule;
        if (params.start !== undefined)
            body.start = params.start;
        if (params.mode !== undefined)
            body.mode = params.mode;
        if (params.is_milestone !== undefined)
            body.is_milestone = params.is_milestone;
        return this.post(`/task/v2/tasks/${parentTaskGuid}/subtasks`, body);
    }
    /**
     * 按嵌套结构创建任务（含 subTasks）。深度优先：先创建父任务再递归创建子任务。
     * 根节点可带 parentTaskGuid 挂到已有任务下。返回嵌套结果及按路径索引的错误列表。
     */
    async createTasksNested(rootItems, options) {
        const maxDepth = options?.maxDepth ?? FeishuTaskService.DEFAULT_MAX_NESTING_DEPTH;
        const errors = [];
        const createOne = async (item, parentGuid, path, depth) => {
            const params = {
                summary: item.summary,
                description: item.description,
                due: item.due,
                completed_at: item.completed_at,
                members: item.members,
                repeat_rule: item.repeat_rule,
                start: item.start,
                mode: item.mode,
                is_milestone: item.is_milestone,
            };
            let created;
            try {
                const res = parentGuid
                    ? await this.createSubtask(parentGuid, params)
                    : await this.createTask(params);
                created = parentGuid ? (res?.subtask ?? res) : (res?.task ?? res);
            }
            catch (e) {
                const msg = e instanceof Error ? e.message : String(e);
                errors.push({ path, error: msg });
                Logger.warn(`创建任务失败 [${path}]: ${msg}`);
                return null;
            }
            const result = { task: created };
            const children = item.subTasks;
            if (children?.length && depth < maxDepth) {
                result.subTasks = [];
                for (let i = 0; i < children.length; i++) {
                    const childPath = `${path}.subTasks[${i}]`;
                    const childResult = await createOne(children[i], created.guid, childPath, depth + 1);
                    if (childResult)
                        result.subTasks.push(childResult);
                }
            }
            else if (children?.length && depth >= maxDepth) {
                Logger.warn(`跳过嵌套子任务 [${path}]: 超过最大深度 ${maxDepth}`);
            }
            return result;
        };
        const results = [];
        for (let i = 0; i < rootItems.length; i++) {
            const item = rootItems[i];
            const one = await createOne(item, item.parentTaskGuid, `[${i}]`, 0);
            if (one)
                results.push(one);
        }
        return { results, errors };
    }
    async updateTask(taskGuid, params) {
        Logger.info(`更新任务: ${taskGuid}`);
        const task = {};
        const updateFields = [];
        if (params.summary !== undefined) {
            task.summary = params.summary;
            updateFields.push('summary');
        }
        if (params.description !== undefined) {
            task.description = params.description;
            updateFields.push('description');
        }
        if (params.due !== undefined) {
            task.due = params.due;
            updateFields.push('due');
        }
        if (params.completed_at !== undefined) {
            task.completed_at = params.completed_at;
            updateFields.push('completed_at');
        }
        if (params.repeat_rule !== undefined) {
            task.repeat_rule = params.repeat_rule;
            updateFields.push('repeat_rule');
        }
        if (params.start !== undefined) {
            task.start = params.start;
            updateFields.push('start');
        }
        if (params.mode !== undefined) {
            task.mode = params.mode;
            updateFields.push('mode');
        }
        if (params.is_milestone !== undefined) {
            task.is_milestone = params.is_milestone;
            updateFields.push('is_milestone');
        }
        if (updateFields.length === 0) {
            throw new Error('update_task requires at least one field to update');
        }
        return this.patch(`/task/v2/tasks/${taskGuid}`, { task, update_fields: updateFields });
    }
    /**
     * 添加任务成员（负责人或关注人）。单次最多 50 个（去重后）；已存在成员会被忽略。
     * POST /task/v2/tasks/:task_guid/add_members
     */
    async addTaskMembers(taskGuid, members) {
        if (!members.length)
            throw new Error('addTaskMembers requires at least one member');
        Logger.info(`添加任务成员: ${taskGuid}, ${members.length} 人`);
        const res = await this.post(`/task/v2/tasks/${taskGuid}/add_members`, { members });
        return res?.data?.task ?? res?.task ?? res;
    }
    /**
     * 移除任务成员（负责人或关注人）。单次 1～500 个；非任务成员会被忽略。
     * POST /task/v2/tasks/:task_guid/remove_members
     */
    async removeTaskMembers(taskGuid, members) {
        if (!members.length)
            throw new Error('removeTaskMembers requires at least one member');
        Logger.info(`移除任务成员: ${taskGuid}, ${members.length} 人`);
        const res = await this.post(`/task/v2/tasks/${taskGuid}/remove_members`, { members });
        return res?.data?.task ?? res?.task ?? res;
    }
    /**
     * 添加任务提醒。任务须已设置截止时间(due)；当前每任务仅支持 1 个提醒，已有提醒时需先调用 removeTaskReminders。
     * POST /task/v2/tasks/:task_guid/add_reminders
     */
    async addTaskReminder(taskGuid, relativeFireMinute) {
        if (relativeFireMinute < 0)
            throw new Error('addTaskReminder relativeFireMinute must be >= 0');
        Logger.info(`添加任务提醒: ${taskGuid}, 截止前 ${relativeFireMinute} 分钟`);
        const res = await this.post(`/task/v2/tasks/${taskGuid}/add_reminders`, {
            reminders: [{ relative_fire_minute: relativeFireMinute }],
        });
        return res?.data?.task ?? res?.task ?? res;
    }
    /**
     * 移除任务提醒。reminder_ids 来自任务详情的 reminders[].id；若提醒不存在会直接返回成功。
     * POST /task/v2/tasks/:task_guid/remove_reminders
     */
    async removeTaskReminders(taskGuid, reminderIds) {
        if (!reminderIds.length)
            throw new Error('removeTaskReminders requires at least one reminder id');
        Logger.info(`移除任务提醒: ${taskGuid}, ${reminderIds.length} 个`);
        const res = await this.post(`/task/v2/tasks/${taskGuid}/remove_reminders`, { reminder_ids: reminderIds });
        return res?.data?.task ?? res?.task ?? res;
    }
    /**
     * 删除任务。删除后无法再获取。需任务可编辑权限。
     * DELETE /task/v2/tasks/:task_guid
     */
    async deleteTask(taskGuid) {
        Logger.info(`删除任务: ${taskGuid}`);
        await this.delete(`/task/v2/tasks/${taskGuid}`);
    }
    /** 列取“我负责的”任务，分页。GET /task/v2/tasks，需 user_access_token。 */
    async listTasks(pageToken, completed, pageSize = 50) {
        const params = { page_size: pageSize, type: 'my_tasks' };
        if (pageToken)
            params.page_token = pageToken;
        if (completed !== undefined)
            params.completed = completed;
        const res = await this.get('/task/v2/tasks', params);
        return {
            items: res?.items ?? [],
            page_token: res?.page_token,
            has_more: Boolean(res?.has_more),
        };
    }
    /** 精简任务项，仅保留常用字段，减少干扰。 */
    static slimTaskItem(task) {
        if (!task || typeof task !== 'object')
            return task;
        return {
            guid: task.guid,
            summary: task.summary,
            description: task.description,
            due: task.due,
            reminders: task.reminders,
            creator: task.creator,
            members: task.members,
            completed_at: task.completed_at,
            status: task.status,
            task_id: task.task_id,
            created_at: task.created_at,
            updated_at: task.updated_at,
            url: task.url,
            start: task.start,
            repeat_rule: task.repeat_rule,
            parent_task_guid: task.parent_task_guid,
            subtask_count: task.subtask_count,
            is_milestone: task.is_milestone,
            mode: task.mode,
        };
    }
    /** 列取任务，每次拉取 2 页（共最多 100 条），返回精简后的 items。 */
    async listTasksTwoPages(pageToken, completed) {
        const PAGE_SIZE = 50;
        const first = await this.listTasks(pageToken, completed, PAGE_SIZE);
        const items = first.items.map(FeishuTaskService.slimTaskItem);
        let nextToken = first.page_token;
        let hasMore = first.has_more;
        if (first.has_more && first.items.length === PAGE_SIZE) {
            const second = await this.listTasks(first.page_token, completed, PAGE_SIZE);
            items.push(...second.items.map(FeishuTaskService.slimTaskItem));
            nextToken = second.page_token;
            hasMore = second.has_more;
        }
        return { items, page_token: nextToken, has_more: hasMore };
    }
}
/** subTasks 最大嵌套层数，防止递归过深。 */
Object.defineProperty(FeishuTaskService, "DEFAULT_MAX_NESTING_DEPTH", {
    enumerable: true,
    configurable: true,
    writable: true,
    value: 10
});
