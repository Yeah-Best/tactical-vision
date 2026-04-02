"""定时刷新英雄版本知识库。

用法：
- 运行一次：python scripts/update_game_knowledge.py --run-once
- 定时轮询：python scripts/update_game_knowledge.py --interval-hours 12
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.game_knowledge_manager import game_knowledge_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def sync_once() -> None:
    snapshot = game_knowledge_service.refresh_knowledge_base()
    logger.info(
        "知识库刷新完成：版本=%s，胜率条目=%s，克制条目=%s",
        snapshot.get("version_label"),
        len(snapshot.get("win_rates", [])),
        len(snapshot.get("counters", [])),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="刷新英雄版本知识库并重建向量索引")
    parser.add_argument("--interval-hours", type=float, default=12.0, help="轮询抓取间隔，单位小时")
    parser.add_argument("--run-once", action="store_true", help="只执行一次抓取与索引构建")
    args = parser.parse_args()

    if args.run_once:
        sync_once()
        return

    interval_seconds = max(args.interval_hours * 3600, 300)
    logger.info("启动定时知识库刷新任务，间隔 %.2f 小时", args.interval_hours)
    while True:
        try:
            sync_once()
        except Exception as exc:
            logger.exception("知识库定时刷新失败：%s", exc)
        logger.info("下次刷新将在 %.2f 小时后执行", interval_seconds / 3600)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
