#!/usr/bin/env node

// Wrapper script to ensure env vars are set before starting the server
process.env.FEISHU_APP_ID = process.env.FEISHU_APP_ID || 'cli_a9462f8ff6b99cc2';
process.env.FEISHU_APP_SECRET = process.env.FEISHU_APP_SECRET || 'kEYzXf9uYmB8hEifIGxNodhCosdbhNXi';
process.env.FEISHU_BASE_URL = process.env.FEISHU_BASE_URL || 'https://open.feishu.cn/open-apis';
process.env.FEISHU_AUTH_TYPE = process.env.FEISHU_AUTH_TYPE || 'tenant';
process.env.NODE_ENV = process.env.NODE_ENV || 'cli';
process.env.PORT = process.env.PORT || '3334';

import('./dist/cli.js');
