# __TITLE__

> Một câu giới thiệu game. Thiết kế đầy đủ nằm trong [design/game-brief.md](design/game-brief.md).

## Chơi

| Phím | Tác dụng |
|---|---|
| … | … |

```bash
gamekit run          # hoặc: make run
```

## Phát triển

```bash
gamekit test         # test unit + integration
gamekit shot         # chạy game và lưu ảnh màn hình vào builds/shots/
gamekit sprites      # nhân vật LPC: assets/source/lpc → SpriteFrames
gamekit export       # build Linux + Windows + Web → builds/dist/
```

Mở Claude Code **trong thư mục này** để dùng các skill của framework (`/prototype`, `/dev-story`, `/next-step`…).

## Thư mục nào của ai

| Phần | Thuộc về | Ghi chú |
|---|---|---|
| `src/`, `assets/`, `tests/`, `design/`, `production/`, `project.godot`, `export_presets.cfg`, `README.md` | **game này** | sửa thoải mái |
| `addons/gamekit/`, `Makefile` | gamekit (`../../tools/gamekit`) | bản sao, sửa ở tools/gamekit rồi `gamekit install` |
| `.claude/`, `CLAUDE.md`, `project.yaml`, `docs/` | framework Claude Code Game Studios | cấu hình agent; cập nhật theo `UPGRADING.md` của template |
| `LICENSES/` | giấy phép của mã bên thứ ba | không xóa |

## Credits

Xem [assets/credits/CREDITS.md](assets/credits/CREDITS.md) (nếu game dùng art LPC).
Framework: [Claude Code Game Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) (MIT, xem `LICENSES/`).
