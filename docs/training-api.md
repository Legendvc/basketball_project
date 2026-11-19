# Day 35 · 训练 API 调用约定

网页通过 `/v2` 读写训练记录。接口文档在服务的 `/v2/docs`，例如本地服务端口为 8003 时，可打开 [Swagger UI](http://127.0.0.1:8003/v2/docs)。

示例使用演练用户 `user_id=1`。这个参数用来指定查询或操作的用户，登录认证将在后续阶段接入。示例中的记录 ID 是 `1`，实际请求应使用接口返回的 ID。

| 操作 | 请求 | 成功响应 |
|---|---|---|
| 新增 | `POST /v2/training`，JSON 含 `user_id`、`training_date`、`shots`、`made` | `201`，新记录 |
| 按日查询 | `GET /v2/training-by-date?user_id=1&training_date=2026-10-15` | `200`，记录列表 |
| 修改 | `PUT /v2/training/1?user_id=1`，JSON 含完整的日期、投篮数和命中数 | `200`，更新后的记录 |
| 删除 | `DELETE /v2/training/1?user_id=1` | `204`，响应体为空 |
| 汇总 | `GET /v2/training-summary?user_id=1&limit=5` | `200`，最近有效训练日的汇总 |

`POST` 和 `PUT` 使用 `Content-Type: application/json`。日期用 `YYYY-MM-DD`。投篮和命中次数都必须是非负整数，命中次数不能超过投篮次数。查询参数里的 `user_id`、`limit` 和路径里的记录 ID 必须为正整数。汇总的 `limit` 默认是 5。

## 一次完整操作

1. 新增训练时发送以下 JSON。服务器返回 `201` 和 `{"id":1,"date":"2026-10-15","shots":10,"made":8}`。请求里的日期键是 `training_date`，单条记录响应里的日期键是 `date`。

   ```json
   {"user_id":1,"training_date":"2026-10-15","shots":10,"made":8}
   ```

2. 按日查询返回以下 JSON。同日可以有多条训练。当天无记录时仍返回 `200`，`records` 为 `[]`。

   ```json
   {
     "user_id": 1,
     "training_date": "2026-10-15",
     "records": [{"id": 1, "date": "2026-10-15", "shots": 10, "made": 8}]
   }
   ```

3. 修改训练时发送以下 JSON，`user_id` 放在查询参数中。服务器返回 `200` 和 `{"id":1,"date":"2026-10-15","shots":12,"made":9}`。

   ```json
   {"training_date":"2026-10-15","shots":12,"made":9}
   ```

4. 刷新汇总。后端先合并同日训练，再判断总投篮数是否达到 5 次，最后取最近 `limit` 个有效训练日。总体命中率按总命中数除以总投篮数计算，保留一位小数。网页可以直接展示返回值。

   ```json
   {
     "has_data": true,
     "training_days": 1,
     "required_training_days": 5,
     "is_reference_only": true,
     "shots": 12,
     "made": 9,
     "percentage": 75.0,
     "days": [{"date": "2026-10-15", "shots": 12, "made": 9, "percentage": 75.0}],
     "warnings": [],
     "notices": [],
     "messages": ["有效训练日不足 5 个，结果仅供参考"]
   }
   ```

5. 删除训练成功后返回 `204`。网页可以直接刷新列表和汇总，跳过对这个响应体的 JSON 解析。

## 常见错误

- `404` 的 `detail` 是字符串。对一条已删除的记录再次发送 `DELETE` 会得到 `{"detail":"训练记录不存在"}`。修改或删除不属于指定用户的记录也返回同样的错误。新增和汇总遇到不存在的用户时返回 `{"detail":"用户不存在"}`。
- `422` 的 `detail` 是数组。输入不合法时，网页可读取错误项中的 `msg`，并根据 `loc` 找到位置。例如，`shots=10`、`made=11` 会得到 `loc: ["body"]` 和 `msg: "Value error, 命中次数不能大于投篮次数"`。
