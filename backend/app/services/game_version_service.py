"""游戏版本信息抓取服务
支持多个游戏平台的版本信息获取
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional, List
import logging
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

# 版本缓存文件路径
VERSION_CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'version_cache.json')

# 默认版本数据（当无法联网抓取时使用）
DEFAULT_VERSIONS = {
    'honor_of_kings': {
        'game_name': '王者荣耀',
        'version': '2.0.0',
        'update_time': '2024.04.01',
        'update_content': '版本更新内容请查看官网',
        'source_url': 'https://pvp.qq.com'
    },
    'lol': {
        'game_name': '英雄联盟',
        'version': '14.6',
        'update_time': '2024.04.01',
        'update_content': '版本更新内容请查看官网',
        'source_url': 'https://lol.qq.com'
    },
    'valorant': {
        'game_name': '无畏契约',
        'version': '8.11',
        'update_time': '2024.04.01',
        'update_content': '版本更新内容请查看官网',
        'source_url': 'https://act.game.qq.com'
    }
}


def load_version_cache() -> Dict:
    """加载版本缓存"""
    try:
        if os.path.exists(VERSION_CACHE_FILE):
            with open(VERSION_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"加载版本缓存失败: {e}")
    return {}


def save_version_cache(data: Dict):
    """保存版本缓存"""
    try:
        os.makedirs(os.path.dirname(VERSION_CACHE_FILE), exist_ok=True)
        with open(VERSION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"保存版本缓存失败: {e}")


class GameVersionService:
    """游戏版本信息抓取服务"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 禁用代理
        self.session = requests.Session()
        self.session.trust_env = False
        # 加载缓存
        self.cached_versions = load_version_cache()

    def get_honor_of_kings_version(self) -> Optional[Dict]:
        """
        获取王者荣耀版本信息

        Returns:
            包含版本号、更新时间、更新内容的字典
        """
        try:
            # 腾讯游戏官网版本更新页面
            url = "https://pvp.qq.com/web201706/newsdetail.shtml?tid=403939"

            response = self.session.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取版本号
            version_match = re.search(r'版本\s*[:：]\s*([0-9.]+)', response.text)
            version = version_match.group(1) if version_match else "未知"

            # 提取更新时间
            date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', response.text)
            update_time = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}" if date_match else "未知"

            # 提取更新内容
            content_div = soup.find('div', class_='art_txt')
            update_content = content_div.get_text(strip=True) if content_div else "无法获取更新内容"

            result = {
                'game_name': '王者荣耀',
                'version': version,
                'update_time': update_time,
                'update_content': update_content[:500],  # 限制长度
                'source_url': url
            }

            # 更新缓存
            self.cached_versions['honor_of_kings'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"获取王者荣耀版本失败: {str(e)}")
            # 返回缓存版本或默认版本
            return self.cached_versions.get('honor_of_kings') or DEFAULT_VERSIONS.get('honor_of_kings')

    def get_lol_version(self) -> Optional[Dict]:
        """
        获取英雄联盟版本信息

        Returns:
            包含版本号、更新时间、更新内容的字典
        """
        try:
            # 英雄联盟官网
            url = "https://lol.qq.com/gicp/news/510/202505/513846.shtml"

            response = self.session.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取版本号
            version_match = re.search(r'([0-9]+\.[0-9]+)', response.text)
            version = version_match.group(1) if version_match else "未知"

            # 提取更新时间
            date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', response.text)
            if date_match:
                update_time = f"{date_match.group(1)}.{date_match.group(2).zfill(2)}.{date_match.group(3).zfill(2)}"
            else:
                update_time = "未知"

            # 提取更新内容
            content_div = soup.find('div', class_='text')
            update_content = content_div.get_text(strip=True) if content_div else "无法获取更新内容"

            result = {
                'game_name': '英雄联盟',
                'version': version,
                'update_time': update_time,
                'update_content': update_content[:500],
                'source_url': url
            }

            # 更新缓存
            self.cached_versions['lol'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"获取英雄联盟版本失败: {str(e)}")
            # 返回缓存版本或默认版本
            return self.cached_versions.get('lol') or DEFAULT_VERSIONS.get('lol')

    def get_valorant_version(self) -> Optional[Dict]:
        """
        获取无畏契约版本信息

        Returns:
            包含版本号、更新时间、更新内容的字典
        """
        try:
            # 无畏契约官网
            url = "https://act.game.qq.com/vas/act/202504/525741/index.html"

            response = self.session.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'

            # 提取版本号
            version_match = re.search(r'([0-9]+\.[0-9]+\.[0-9]+)', response.text)
            version = version_match.group(1) if version_match else "未知"

            # 提取更新时间
            date_match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', response.text)
            if date_match:
                update_time = f"{date_match.group(1)}.{date_match.group(2).zfill(2)}.{date_match.group(3).zfill(2)}"
            else:
                update_time = "未知"

            result = {
                'game_name': '无畏契约',
                'version': version,
                'update_time': update_time,
                'update_content': "请访问官网查看详细更新内容",
                'source_url': url
            }

            # 更新缓存
            self.cached_versions['valorant'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"获取无畏契约版本失败: {str(e)}")
            # 返回缓存版本或默认版本
            return self.cached_versions.get('valorant') or DEFAULT_VERSIONS.get('valorant')

    def get_game_versions(self, games: List[str] = None) -> List[Dict]:
        """
        获取多个游戏的版本信息

        Args:
            games: 游戏名称列表，如果为 None 则获取所有支持的游戏

        Returns:
            版本信息列表
        """
        if games is None:
            games = ['honor_of_kings', 'lol', 'valorant']

        version_info = []
        game_methods = {
            'honor_of_kings': self.get_honor_of_kings_version,
            'lol': self.get_lol_version,
            'valorant': self.get_valorant_version
        }

        for game in games:
            method = game_methods.get(game)
            if method:
                info = method()
                if info:
                    version_info.append(info)

        return version_info


# 全局服务实例
game_version_service = GameVersionService()


def get_latest_game_version(game_name: str = 'honor_of_kings') -> Optional[Dict]:
    """
    获取指定游戏的最新版本信息

    Args:
        game_name: 游戏名称 (honor_of_kings, lol, valorant)

    Returns:
        版本信息字典
    """
    method_map = {
        'honor_of_kings': game_version_service.get_honor_of_kings_version,
        '王者荣耀': game_version_service.get_honor_of_kings_version,
        'lol': game_version_service.get_lol_version,
        '英雄联盟': game_version_service.get_lol_version,
        'valorant': game_version_service.get_valorant_version,
        '无畏契约': game_version_service.get_valorant_version
    }

    method = method_map.get(game_name)
    if method:
        return method()
    return None


if __name__ == "__main__":
    # 测试代码
    print("测试游戏版本抓取...")

    # 测试王者荣耀
    print("\n=== 王者荣耀 ===")
    hok_version = get_latest_game_version('honor_of_kings')
    if hok_version:
        print(f"游戏: {hok_version['game_name']}")
        print(f"版本: {hok_version['version']}")
        print(f"更新时间: {hok_version['update_time']}")
        print(f"更新内容: {hok_version['update_content']}")

    # 测试英雄联盟
    print("\n=== 英雄联盟 ===")
    lol_version = get_latest_game_version('lol')
    if lol_version:
        print(f"游戏: {lol_version['game_name']}")
        print(f"版本: {lol_version['version']}")
        print(f"更新时间: {lol_version['update_time']}")

    # 获取所有游戏
    print("\n=== 所有游戏版本 ===")
    all_versions = game_version_service.get_game_versions()
    for v in all_versions:
        print(f"{v['game_name']}: v{v['version']} ({v['update_time']})")
