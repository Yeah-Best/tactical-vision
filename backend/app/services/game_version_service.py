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
        """静态返回王者荣耀版本信息（比赛专用极稳版，不依赖外部网络）"""
        try:
            # ==========================================
            # ⚠️ 比赛前必看：请在比赛前一晚，手动更新这里的版本号！
            # ==========================================
            current_version = "S43赛季" # <-- 修改为比赛当天的实际版本（如 "S35赛季 3.6.1"）
            
            result = {
                'game_name': '王者荣耀',
                'version': current_version,
                'update_time': datetime.now().strftime("%Y.%m.%d"), # 自动获取当前日期
                'update_content': f"为保障系统稳定，已配置为本地直读模式。当前采用 {current_version} 版本数据，详细英雄和装备改动请参考官网。",
                'source_url': 'https://pvp.qq.com'
            }

            # 依然保留写入缓存的逻辑，保持系统一致性
            self.cached_versions['honor_of_kings'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"加载王者荣耀静态版本失败: {str(e)}")
            # 最极端的兜底，读取文件最上方的 DEFAULT_VERSIONS
            return DEFAULT_VERSIONS.get('honor_of_kings')

    def get_lol_version(self) -> Optional[Dict]:
        """使用拳头官方 Data Dragon API 获取英雄联盟最新版本信息 (极度稳定，适合比赛)"""
        try:
            # 1. 请求 Riot 官方的 Data Dragon 版本接口
            api_url = "https://ddragon.leagueoflegends.com/api/versions.json"
            
            # 这个接口极度稳定且没有反爬机制，5秒超时足够了
            response = self.session.get(api_url, headers=self.headers, timeout=5)
            response.raise_for_status() # 确保状态码是 200
            
            # 2. 解析返回的 JSON 数组
            # 格式类似于: ["14.7.1", "14.6.1", ...]，第一个就是最新版本
            versions = response.json()
            if not versions or not isinstance(versions, list):
                raise ValueError("Data Dragon API 返回的数据格式异常")
                
            latest_version = versions[0]
            
            # 提取主版本号作为显示 (例如 "14.7.1" -> 提取 "14.7" 或者直接保留 "14.7.1")
            # 这里我们直接保留完整的 "14.7.1" 以保证准确性

            result = {
                'game_name': '英雄联盟',
                'version': latest_version,
                'update_time': datetime.now().strftime("%Y.%m.%d"), # Data Dragon 不返回更新日期，统一使用当前系统时间
                'update_content': f"已通过拳头官方接口同步至最新 {latest_version} 版本。详细改动请查看官网公告。",
                'source_url': "https://lol.qq.com" # 为了统一规范，来源链接依然指向国服官网
            }

            # 3. 更新并保存本地缓存
            self.cached_versions['lol'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"抓取英雄联盟官方 Data Dragon 版本失败: {str(e)}")
            # 如果极端情况下断网，直接返回本地缓存或默认兜底版本，绝不崩溃
            return self.cached_versions.get('lol') or DEFAULT_VERSIONS.get('lol')

    def get_valorant_version(self) -> Optional[Dict]:
        """使用第三方稳定 API 获取无畏契约版本信息"""
        try:
            # 这是一个全球开发者广泛使用的高优接口，返回纯 JSON，无反爬
            api_url = "https://valorant-api.com/v1/version"
            
            response = self.session.get(api_url, headers=self.headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # 返回格式示例: {"data": {"branch": "release-08.05", "version": "08.05.00.234567"}}
            # 提取 branch 并处理，例如 "release-08.05" -> "8.05"
            branch = data.get("data", {}).get("branch", "最新")
            version = branch.replace("release-0", "").replace("release-", "")

            result = {
                'game_name': '无畏契约',
                'version': version,
                'update_time': datetime.now().strftime("%Y.%m.%d"),
                'update_content': f"已通过 API 同步至 {version} 版本。详细更新请前往官网查看。",
                'source_url': "https://val.qq.com/"
            }

            self.cached_versions['valorant'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"抓取无畏契约稳定 API 失败: {str(e)}")
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
