# Movie-ClassiSearch API 文档

## 基础信息

- 基础URL: `http://localhost:5000`
- 所有响应均为 JSON 格式
- 所有请求使用 GET 方法

## API 端点

### 1. 搜索电影

搜索电影信息，支持多字段组合搜索。

**端点:** `/api/search`

**参数:**

- `query` (string): 搜索查询字符串
  - 支持的字段前缀：title:, director:, actor:, plot:
  - 如果没有指定字段前缀，默认搜索标题
- `page` (integer, 可选): 页码，默认为 1
- `page_size` (integer, 可选): 每页结果数，默认为 50

**示例请求:**

```http
GET /api/search?query=title:%20De%20pai%20para%20FIlho%20director:%20Paulo%20Halm&page=1&page_size=20
GET /api/search?query=actor:%20Tom%20Hanks&page=1&page_size=20
GET /api/search?query=Inception // 直接搜索标题
```

**响应格式:**

```json
{
"total": 100, // 总结果数
"page": 1, // 当前页码
"page_size": 20, // 每页结果数
"total_pages": 5, // 总页数
"results": [ // 电影列表
{
"id": "tt0000001",
"title": "电影标题",
"director": "导演名称",
"plot": "剧情简介",
"score": 8.5,
"release_date": "2023-01-01",
"poster": "海报URL",
"actors": "演员1,演员2",
"genres": "类型1,类型2"
}
// ...更多电影
]
}
```

### 2. 获取电影推荐

获取电影推荐列表，支持分类筛选和排序。

**端点:** `/api/movies`

**参数:**

- `category` (string, 可选): 电影类型
- `sort_by` (string, 可选): 排序方式
  - 支持的值：'score'（评分）, 'date'（日期）
  - 可组合使用，如 'score,date'
  - 默认按评分排序
- `page` (integer, 可选): 页码，默认为 1
- `page_size` (integer, 可选): 每页结果数，默认为 20

**示例请求:**

```http
GET /api/movies?category=Action&sort_by=score&page=1&page_size=20
GET /api/movies?sort_by=date
GET /api/movies?sort_by=score,date
```

**响应格式:**

```json
{
"total": 100,
"page": 1,
"page_size": 20,
"total_pages": 5,
"results": [
{
"id": "tt0000001",
"title": "电影标题",
"director": "导演名称",
"plot": "剧情简介",
"score": 8.5,
"release_date": "2023-01-01",
"poster": "海报URL",
"actors": "演员1,演员2",
"genres": "类型1,类型2"
}
// ...更多电影
]
}
```

### 3. 获取电影类型列表

获取所有可用的电影类型。

**端点:** `/api/genres`

**参数:** 无

**示例请求:**

```http
GET /api/genres
```

**响应格式:**

```json
{
"genres": [
"Action",
"Comedy",

"Drama",

// ...更多类型
]
}
```

## 错误处理

所有API在发生错误时会返回相应的HTTP状态码和错误信息：

```json
{
"error": "错误信息描述"
}
```

**常见状态码:**

- 200: 请求成功
- 404: 资源未找到
- 500: 服务器内部错误

## 注意事项

1. 所有日期格式为 "YYYY-MM-DD"
2. 分页从第1页开始
3. 搜索查询支持部分匹配
4. 评分范围为 0-10
5. 所有文本编码使用 UTF-8
