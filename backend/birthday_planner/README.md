# 测试不同模型的流的输出支持，测试支持gemini和deepseek流
升级到最新版a2a-sdk==0.2.10，和google-adk==1.5.0

# 旧版本发现，流式效果没有，只有在模型的最后时，才统一将结果返回。
```
google-adk>=1.0.0,<2.0.0
a2a-sdk==0.2.5
```


# 测试过程
修改环境变量, 注意STREAMING=true，表示流式输出
cp env_template .env

启动服务端
python main_api.py

启动客户端
python a2a_client.py

# 不同版本的a2a和adk导致的输出问题，仔细观察输出的时间
最新版a2a-sdk==0.2.10，和google-adk==1.5.0正确的流输出
```
1751505432.866287
{'id': 'eff0fbf28df04bb08c2a618d8d388efb', 'jsonrpc': '2.0', 'result': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'final': False, 'kind': 'status-update', 'status': {'state': 'submitted', 'timestamp': '2025-07-03T01:17:12.812458+00:00'}, 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}}
1751505432.866656
{'id': 'eff0fbf28df04bb08c2a618d8d388efb', 'jsonrpc': '2.0', 'result': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'final': False, 'kind': 'status-update', 'status': {'state': 'working', 'timestamp': '2025-07-03T01:17:12.812567+00:00'}, 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}}
1751505433.670728
{'id': 'eff0fbf28df04bb08c2a618d8d388efb', 'jsonrpc': '2.0', 'result': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'final': False, 'kind': 'status-update', 'status': {'message': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'kind': 'message', 'messageId': '0cebe52d-826c-4ff2-ba26-623c5d200c74', 'parts': [{'kind': 'text', 'text': '请'}], 'role': 'agent', 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}, 'state': 'working', 'timestamp': '2025-07-03T01:17:13.667822+00:00'}, 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}}
1751505433.784075
{'id': 'eff0fbf28df04bb08c2a618d8d388efb', 'jsonrpc': '2.0', 'result': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'final': False, 'kind': 'status-update', 'status': {'message': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'kind': 'message', 'messageId': '2e95d9e5-41c7-466e-be99-1b11d9c1235a', 'parts': [{'kind': 'text', 'text': '告诉我更多关于生日的信息。\n- 场地\n- 举办派对的时间\n-'}], 'role': 'agent', 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}, 'state': 'working', 'timestamp': '2025-07-03T01:17:13.781191+00:00'}, 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}}
1751505433.905635
{'id': 'eff0fbf28df04bb08c2a618d8d388efb', 'jsonrpc': '2.0', 'result': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'final': False, 'kind': 'status-update', 'status': {'message': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'kind': 'message', 'messageId': 'b954810f-7f3f-4abc-a394-6234a9b3aeed', 'parts': [{'kind': 'text', 'text': ' 适合年龄的活动\n- 聚会的主题'}], 'role': 'agent', 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}, 'state': 'working', 'timestamp': '2025-07-03T01:17:13.903806+00:00'}, 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}}
1751505433.91151
{'id': 'eff0fbf28df04bb08c2a618d8d388efb', 'jsonrpc': '2.0', 'result': {'artifact': {'artifactId': '568b9190-0247-4f30-ab26-1ea6075cfd2c', 'parts': [{'kind': 'text', 'text': '请告诉我更多关于生日的信息。\n- 场地\n- 举办派对的时间\n- 适合年龄的活动\n- 聚会的主题'}]}, 'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'kind': 'artifact-update', 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}}
1751505433.9122272
{'id': 'eff0fbf28df04bb08c2a618d8d388efb', 'jsonrpc': '2.0', 'result': {'contextId': 'd8d6a310-ab05-407e-aae2-3e342d96181f', 'final': True, 'kind': 'status-update', 'status': {'state': 'completed', 'timestamp': '2025-07-03T01:17:13.908831+00:00'}, 'taskId': '367c7f57-2683-4ef3-9b26-23aa49293e54'}}
```