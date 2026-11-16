# __TITLE__: hướng dẫn cho mọi AI agent

Game này dùng framework Claude Code Game Studios. Hướng dẫn đầy đủ nằm trong các file dưới đây;
agent nào cũng đọc theo cùng một thứ tự:

1. `CLAUDE.md`: cấu hình framework. Các dòng `@đường/dẫn` trong đó là file cần đọc kèm, ví dụ
   `@.claude/docs/coding-standards.md` nghĩa là đọc `.claude/docs/coding-standards.md`.
   Phần "This game" ở đầu file áp dụng trước tiên.
2. `README.md`: game là gì, phím, cấu trúc, thư mục nào thuộc về ai.
3. `../../AGENTS.md`: workflow của workspace (yêu cầu → công cụ, **quy tắc commit**).

Skill: `.claude/skills/<tên>/SKILL.md`, cũng xem được qua `.agents/skills/` (symlink).
Lệnh `/tên` trong tài liệu nghĩa là đọc rồi làm theo `SKILL.md` của skill đó. Các skill này viết cho Claude Code:
phần nào dùng hook, subagent hay hộp thoại hỏi người dùng thì agent khác tự làm bước tương đương, ví dụ tự
chạy kiểm tra mà hook vẫn chạy, hoặc hỏi người dùng bằng tin nhắn thường.

Công cụ: `gamekit` (xem `gamekit help`). Không sửa `addons/gamekit/`, vì đó là bản sao.
