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
        """真正动态获取王者荣耀最新版本信息"""
        try:
            # 1. 先抓取官网版本公告的“列表页”
            list_url = "https://pvp.qq.com/webplat/info/news_version3_list/152/1163/1737.shtml"
            list_response = self.session.get(list_url, headers=self.headers, timeout=10)
            list_response.encoding = 'gbk' # 王者官网一般是GBK编码
            list_soup = BeautifulSoup(list_response.text, 'html.parser')
            
            # 2. 动态寻找列表中的第一条（最新）版本更新新闻
            latest_article_url = None
            # 尝试匹配官网新闻列表的 a 标签
            for a_tag in list_soup.select('a.news_txt, .news-list a, .list-item a'):
                title = a_tag.get_text()
                # 过滤关键字，确保是版本更新公告
                if '更新' in title or '版本' in title or '不停机' in title:
                    href = a_tag.get('href')
                    if href:
                        # 拼接完整URL
                        latest_article_url = href if href.startswith('http') else f"https://pvp.qq.com{href}"
                        break
            
            if not latest_article_url:
                raise ValueError("未能从官网列表页提取到最新的版本公告链接")

            # 3. 抓取动态获取到的最新文章正文
            response = self.session.get(latest_article_url, headers=self.headers, timeout=10)
            response.encoding = 'gbk'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取版本号
            version_match = re.search(r'[Vv]?([0-9]+\.[0-9]+\.[0-9]+|[0-9]+\.[0-9]+)', response.text)
            version = version_match.group(1) if version_match else "最新版本"

            # 提取更新时间
            date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', response.text)
            update_time = f"{date_match.group(1)}.{date_match.group(2)}.{date_match.group(3)}" if date_match else datetime.now().strftime("%Y.%m.%d")

            # 提取正文内容 (支持官网常见的两种正文 class)
            content_div = soup.find('div', class_='art_txt') or soup.find('div', class_='detail-cont')
            update_content = content_div.get_text(strip=True) if content_div else "无法获取更新内容正文"

            result = {
                'game_name': '王者荣耀',
                'version': version,
                'update_time': update_time,
                'update_content': update_content[:500] + '...', # 截取前500字防止爆Token
                'source_url': latest_article_url
            }

            # 更新缓存
            self.cached_versions['honor_of_kings'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"真实抓取王者荣耀版本失败: {str(e)}")
            return self.cached_versions.get('honor_of_kings') or DEFAULT_VERSIONS.get('honor_of_kings')

    def get_lol_version(self) -> Optional[Dict]:
        """真正动态获取英雄联盟（国服）最新版本信息"""
        try:
            # 1. 请求腾讯官方的通用新闻列表API (频道号4913通常对应LOL版本更新)
            # 相比于直接解析可能被JS动态渲染屏蔽的HTML，直接请求底层数据接口最稳妥
            api_url = "https://apps.game.qq.com/cmc/cross?serviceId=3&source=web_pc&filter=channel&chanid=4913&typeids=1&limit=5&start=0"
            
            # 由于腾讯接口返回的是类似 var data = {...} 的JSONP格式，需要做字符串截取
            list_response = self.session.get(api_url, headers=self.headers, timeout=10)
            list_text = list_response.text
            
            # 提取有效JSON部分
            json_str = re.search(r'\{.*\}', list_text, re.DOTALL)
            if not json_str:
                raise ValueError("未能解析LOL官方新闻列表API")
                
            data = json.loads(json_str.group(0))
            articles = data.get('data', {}).get('msg', [])
            
            latest_article = None
            for item in articles:
                if '版本' in item.get('sTitle', '') or '更新' in item.get('sTitle', ''):
                    latest_article = item
                    break
                    
            if not latest_article:
                raise ValueError("未能找到最新的LOL版本公告")

            # 2. 拼接最新文章的真实URL并提取信息
            article_url = f"https://lol.qq.com/news/detail.shtml?docid={latest_article.get('iDocID')}"
            title = latest_article.get('sTitle', '')
            
            # 从标题中提取版本号 (如 "14.6版本更新公告" -> "14.6")
            version_match = re.search(r'([0-9]+\.[0-9]+)', title)
            version = version_match.group(1) if version_match else "最新版本"

            result = {
                'game_name': '英雄联盟',
                'version': version,
                'update_time': latest_article.get('sCreated', '').split(' ')[0].replace('-', '.'),
                'update_content': title + "，详细改动请查看官网公告。", # LOL的新闻正文是动态加载的，这里用标题作为摘要
                'source_url': article_url
            }

            # 更新缓存
            self.cached_versions['lol'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"真实抓取英雄联盟版本失败: {str(e)}")
            return self.cached_versions.get('lol') or DEFAULT_VERSIONS.get('lol')

    def get_valorant_version(self) -> Optional[Dict]:
        """真正动态获取无畏契约（国服）最新版本信息"""
        try:
            # 1. 策略：无畏契约官网会在初始化的 HTML 中包含最新的新闻列表数据用于首屏渲染
            url = "https://val.qq.com/"
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            # 尝试通过正则直接从页面源文件提取包含"版本更新公告"的标题
            # 匹配格式如："9.04版本更新公告" 或 "v8.11版本更新公告"
            version_match = re.search(r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s*版本更新公告', response.text)
            
            if version_match:
                version = version_match.group(1)
            else:
                # 兜底：尝试访问另一个常见的新闻聚合页
                list_url = "https://val.qq.com/web202305/news.html"
                list_response = self.session.get(list_url, headers=self.headers, timeout=10)
                list_response.encoding = 'utf-8'
                version_match = re.search(r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s*版本更新公告', list_response.text)
                version = version_match.group(1) if version_match else "最新版本"
                
            # 获取当前时间作为兜底更新时间（版本更新通常在查询的近期）
            update_time = datetime.now().strftime("%Y.%m.%d")
            
            result = {
                'game_name': '无畏契约',
                'version': version,
                'update_time': update_time,
                'update_content': f"发现 {version} 版本更新。详细更新日志、英雄调整和地图改动请前往《无畏契约》官网 (val.qq.com) 新闻中心查看。",
                'source_url': "https://val.qq.com/web202305/news.html"
            }

            # 更新缓存
            self.cached_versions['valorant'] = result
            save_version_cache(self.cached_versions)

            return result

        except Exception as e:
            logger.error(f"真实抓取无畏契约版本失败: {str(e)}")
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
