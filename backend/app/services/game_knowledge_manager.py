"""
游戏知识库管理器
支持多游戏类型的动态切换
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import chromadb
except RuntimeError as e:
    if "sqlite" in str(e).lower():
        logger.warning("SQLite版本过低，ChromaDB功能将被禁用：%s", e)
        chromadb = None
    else:
        raise
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import HashingVectorizer


class BaseGameKnowledgeService(ABC):
    """游戏知识库服务基类"""

    def __init__(self):
        self.base_dir = Path(settings.GAME_KNOWLEDGE_DIR).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir = self.base_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_path = self.base_dir / "knowledge_snapshot.json"
        self.chroma_path = self.base_dir / "chroma"
        self.vectorizer = HashingVectorizer(
            n_features=1024,
            alternate_sign=False,
            norm="l2",
            ngram_range=(1, 2),
        )
        self.http = requests.Session()
        self.http.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            }
        )

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def _request_text(self, url: str) -> str:
        response = self.http.get(url, timeout=settings.GAME_KNOWLEDGE_REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        return response.text

    @abstractmethod
    def refresh_knowledge_base(self) -> Dict[str, Any]:
        """刷新知识库"""
        pass

    @abstractmethod
    def ensure_knowledge_base(self) -> Dict[str, Any]:
        """确保知识库可用"""
        pass

    @abstractmethod
    def build_review_context(
        self,
        *,
        game_type: str,
        game_description: str,
        game_result: Optional[str] = None,
        kda: Optional[str] = None,
        team_composition: Optional[List[str]] = None,
        enemy_composition: Optional[List[str]] = None,
        game_version: Optional[str] = None,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """构建复盘上下文"""
        pass


class HonorKingsKnowledgeService(BaseGameKnowledgeService):
    """王者荣耀知识库服务"""

    PATCH_INDEX_URL = "https://pvp.qq.com/webplat/info/news_version3_list/152/1163/1737.shtml"
    WIN_RATE_URL = "https://pvp.qq.com/web201605/herolist.shtml"
    HERO_DETAIL_URL = "https://pvp.qq.com/web201605/herodetail/{hero_id}.shtml"
    KING_API_VERSION_URL = "https://game.gtimg.cn/images/yxzjs/img202409/heroimg/hero_list.json"

    def __init__(self):
        super().__init__()
        self.http.headers.update({"Referer": "https://pvp.qq.com/"})
        self.game_name = "王者荣耀"
        self.game_code = "honor_kings"
        self.collection_name = "honorkings_patch_knowledge"


    def _embed_texts(self, texts):
        """生成文本向量"""
        from sklearn.feature_extraction.text import HashingVectorizer
        matrix = self.vectorizer.transform(list(texts))
        return matrix.astype("float32").toarray().tolist()

    def _get_client(self):
        if chromadb is None:
            raise RuntimeError("ChromaDB不可用，请升级SQLite版本")
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        return chromadb.PersistentClient(path=str(self.chroma_path))

    def _get_collection(self, reset: bool = False):
        if chromadb is None:
            return None
        client = self._get_client()
        if reset:
            try:
                client.delete_collection(self.collection_name)
            except Exception:
                pass
        return client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _extract_patch_meta(self) -> Dict[str, Any]:
        """从王者荣耀官网抓取最新版本信息"""
        try:
            html = self._request_text(self.PATCH_INDEX_URL)
            soup = BeautifulSoup(html, "html.parser")

            # 查找版本公告标题
            version_items = []
            for item in soup.select(".news-list li, .version-list li, .article-item"):
                title_tag = item.select_one("a, h3, .title")
                if not title_tag:
                    continue

                title = self._clean_text(title_tag.get_text(" ", strip=True))
                link = item.select_one("a")

                # 匹配版本号格式
                version_match = re.search(r"[Vv](\d+(?:\.\d+)*)|(\d{4}\.\d+)|(\d{8})", title)
                version_label = version_match.group(0) if version_match else "最新版本"

                if not link or not link.get("href"):
                    continue

                href = link["href"]
                if not href.startswith("http"):
                    href = urljoin("https://pvp.qq.com/", href)

                version_items.append({
                    "title": title,
                    "url": href,
                    "version_label": version_label,
                })

                if len(version_items) >= 5:
                    break

            if not version_items:
                logger.warning("未能从官网抓取到版本信息，使用默认版本")
                return {
                    "title": "王者荣耀版本公告",
                    "url": self.PATCH_INDEX_URL,
                    "version_label": "当前版本",
                }

            latest = version_items[0]
            logger.info("识别到最新补丁版本：%s", latest["version_label"])
            return latest

        except Exception as exc:
            logger.error("抓取版本公告异常：%s", exc)
            return {
                "title": "王者荣耀版本公告",
                "url": self.PATCH_INDEX_URL,
                "version_label": "当前版本",
            }

    def _extract_patch_notes(self, patch_meta: Dict[str, Any]) -> Dict[str, Any]:
        """提取版本公告详情"""
        try:
            html = self._request_text(patch_meta["url"])
            soup = BeautifulSoup(html, "html.parser")

            # 提取正文内容
            texts: List[str] = []
            content_selectors = [
                ".news-content p",
                ".article-content p",
                ".detail-content p",
                ".version-detail p",
                "main p",
                ".content p",
                "article p",
            ]

            for selector in content_selectors:
                nodes = soup.select(selector)
                if nodes:
                    for node in nodes:
                        text = self._clean_text(node.get_text(" ", strip=True))
                        if len(text) >= 8:
                            texts.append(text)
                    if texts:
                        break

            # 如果没找到段落，提取所有文本
            if not texts:
                text_nodes = soup.select("div, p, span")
                for node in text_nodes:
                    text = self._clean_text(node.get_text(" ", strip=True))
                    if len(text) >= 8 and len(text) <= 500:
                        texts.append(text)
                    if len(texts) >= 30:
                        break

            # 去重并限制数量
            unique_texts = []
            seen = set()
            for text in texts:
                if text not in seen:
                    seen.add(text)
                    unique_texts.append(text)
                if len(unique_texts) >= 20:
                    break

            if not unique_texts:
                unique_texts = [
                    f"当前版本为 {patch_meta['version_label']}，详细更新内容请访问官网查看。"
                ]

            summary = " ".join(unique_texts[:8])
            return {
                "title": patch_meta["title"],
                "url": patch_meta["url"],
                "version_label": patch_meta["version_label"],
                "summary": summary,
                "sections": unique_texts,
            }

        except Exception as exc:
            logger.warning("提取版本公告详情失败：%s", exc)
            return {
                "title": patch_meta["title"],
                "url": patch_meta["url"],
                "version_label": patch_meta["version_label"],
                "summary": f"当前版本为 {patch_meta['version_label']}",
                "sections": [f"当前版本为 {patch_meta['version_label']}"],
            }

    def _fetch_champion_mappings(self) -> List[Dict[str, Any]]:
        """抓取王者荣耀英雄列表映射"""
        try:
            html = self._request_text(self.WIN_RATE_URL)
            soup = BeautifulSoup(html, "html.parser")

            hero_list = soup.select(".herolist li, .hero-list li, [class*='hero-item']")
            if not hero_list:
                try:
                    hero_json = self._request_text(self.KING_API_VERSION_URL)
                    hero_data = json.loads(hero_json)
                    mappings = []
                    for hero in hero_data:
                        hero_id = hero.get("heroId", hero.get("id", ""))
                        hero_name = hero.get("heroName", hero.get("name", ""))
                        hero_title = hero.get("heroTitle", hero.get("title", ""))
                        english_name = self._pinyin(hero_name)

                        mappings.append({
                            "champion_id": str(hero_id),
                            "english_name": english_name,
                            "chinese_name": hero_name,
                            "hero_title": hero_title,
                            "aliases": [hero_id, hero_name, hero_title, english_name],
                        })
                    logger.info("从JSON接口获取到 %d 个英雄", len(mappings))
                    return mappings
                except Exception as e:
                    logger.warning("从JSON接口获取英雄失败：%s", e)

            # 从HTML解析
            mappings = []
            for hero_item in hero_list:
                link = hero_item.select_one("a")
                if not link:
                    continue

                href = link.get("href", "")
                hero_id_match = re.search(r"heroId=(\d+)", href)
                hero_id = hero_id_match.group(1) if hero_id_match else ""

                hero_name = self._clean_text(hero_item.get_text(" ", strip=True))
                if not hero_name:
                    continue

                english_name = self._pinyin(hero_name)

                mappings.append({
                    "champion_id": hero_id,
                    "english_name": english_name,
                    "chinese_name": hero_name,
                    "hero_title": "",
                    "aliases": [hero_id, hero_name, english_name],
                })

            logger.info("从HTML获取到 %d 个英雄", len(mappings))
            return mappings

        except Exception as exc:
            logger.error("抓取英雄映射失败：%s", exc)
            return self._get_default_hero_mappings()

    @staticmethod
    def _pinyin(text: str) -> str:
        """简单的中文转拼音（基础实现）"""
        pinyin_map = {
            "亚瑟": "Arthur", "妲己": "Daji", "李白": "Libai", "貂蝉": "Diaochan",
            "韩信": "Hanxin", "鲁班七号": "Luban", "后羿": "Houyi", "孙悟空": "Wukong",
            "程咬金": "Chengyaojin", "赵云": "Zhaoyun", "小乔": "Xiaoqiao", "周瑜": "Zhouyu",
            "安琪拉": "Anqila", "王昭君": "Wangzhaojun", "甄姬": "Zhenji", "蔡文姬": "Caiwenji",
            "兰陵王": "Lanlingwang", "阿轲": "Ake", "孙尚香": "Sunshangxiang", "虞姬": "Yuji",
            "扁鹊": "Bianque", "庄周": "Zhuangzhou", "钟馗": "Zhongkui", "芈月": "Miyue",
            "高渐离": "Gaojianli", "不知火舞": "Buzhihuowu", "娜可露露": "Nakolulu",
        }
        return pinyin_map.get(text, "Unknown")

    def _get_default_hero_mappings(self) -> List[Dict[str, Any]]:
        """默认英雄映射（当抓取失败时使用）"""
        default_heroes = [
            {"champion_id": "1", "english_name": "Arthur", "chinese_name": "亚瑟", "hero_title": "圣骑士", "aliases": ["1", "亚瑟", "Arthur"]},
            {"champion_id": "2", "english_name": "Daji", "chinese_name": "妲己", "hero_title": "魅惑妖姬", "aliases": ["2", "妲己", "Daji"]},
            {"champion_id": "3", "english_name": "Libai", "chinese_name": "李白", "hero_title": "青莲剑仙", "aliases": ["3", "李白", "Libai"]},
            {"champion_id": "4", "english_name": "Diaochan", "chinese_name": "貂蝉", "hero_title": "绝代舞姬", "aliases": ["4", "貂蝉", "Diaochan"]},
            {"champion_id": "5", "english_name": "Hanxin", "chinese_name": "韩信", "hero_title": "国士无双", "aliases": ["5", "韩信", "Hanxin"]},
            {"champion_id": "6", "english_name": "Luban", "chinese_name": "鲁班七号", "hero_title": "机关造物", "aliases": ["6", "鲁班七号", "Luban"]},
            {"champion_id": "7", "english_name": "Houyi", "chinese_name": "后羿", "hero_title": "射落九日", "aliases": ["7", "后羿", "Houyi"]},
            {"champion_id": "8", "english_name": "Wukong", "chinese_name": "孙悟空", "hero_title": "齐天大圣", "aliases": ["8", "孙悟空", "Wukong"]},
        ]
        logger.warning("使用默认英雄映射，共 %d 个英雄", len(default_heroes))
        return default_heroes

    def _fetch_win_rates(self, champion_mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        真实的英雄数据抓取（替换掉之前的 hash 伪造数据）
        注：真实胜率被封锁在营地APP，此处改为抓取真实官方接口的英雄定位属性作为 RAG 知识库支撑。
        """
        results = []
        try:
            # 真实请求官方公开的英雄基础数据接口
            api_url = "https://game.gtimg.cn/images/yxzjs/img202409/heroimg/hero_list.json"
            response = self.http.get(api_url, timeout=10)
            hero_data_list = response.json()
            
            # 转为字典方便 O(1) 查找
            hero_data_map = {str(item.get('heroId', '')): item for item in hero_data_list}

            # 常见官方职业枚举映射
            type_map = {1: "战士", 2: "法师", 3: "坦克", 4: "刺客", 5: "射手", 6: "辅助"}

            for hero in champion_mappings:
                hero_id = str(hero.get("champion_id", ""))
                hero_name = hero.get("chinese_name", "")
                
                official_data = hero_data_map.get(hero_id)
                if not official_data:
                    continue

                hero_type = official_data.get('heroType', '0')
                hero_type_cn = type_map.get(int(hero_type), "未知") if str(hero_type).isdigit() else hero_type

                results.append({
                    "hero": hero_name,
                    "hero_cn": hero_name,
                    "hero_en": hero["english_name"],
                    "win_rate": "暂无",
                    "pick_rate": "暂无",
                    "ban_rate": "暂无",
                    # 将编造的数据替换为真实的官方属性说明
                    "raw": f"官方真实定位: 【{hero_type_cn}】。英雄特色称号：{official_data.get('heroTitle', '未知')}。",
                    "source_url": api_url,
                })
                
            logger.info("成功抓取了 %d 个英雄的真实官方属性数据", len(results))
            return results
        except Exception as exc:
            logger.warning("抓取真实英雄数据失败：%s", exc)
            return []

    def _fetch_counters(self, champion_mappings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """真正抓取王者荣耀官网英雄详情页的克制关系"""
        results = []
        # 控制并发或抓取数量防止被限制
        logger.info("开始深入抓取官网英雄克制关系，预计需要几十秒时间...")
        
        for hero in champion_mappings:
            hero_id = hero.get("champion_id")
            hero_name = hero.get("chinese_name")
            if not hero_id:
                continue

            try:
                # 真实访问官网的单个英雄详情页
                detail_url = f"https://pvp.qq.com/web201605/herodetail/{hero_id}.shtml"
                response = self.http.get(detail_url, timeout=5)
                response.encoding = 'gbk'
                soup = BeautifulSoup(response.text, 'html.parser')

                counters_list = []
                countered_by_list = []
                
                # 寻找官网页面中 "搭档/压制/被压制" 的模块
                rel_box = soup.select('.hero-rel-box .hero-rel-list')
                if len(rel_box) >= 3:
                    # 官网固定排版：索引1为"压制英雄"，索引2为"被压制英雄"
                    counters_tags = rel_box[1].select('a')
                    countered_by_tags = rel_box[2].select('a')
                    
                    for a in counters_tags:
                        hero_text = a.get('title') or a.get_text(strip=True)
                        if hero_text:
                            counters_list.append(hero_text)
                            
                    for a in countered_by_tags:
                        hero_text = a.get('title') or a.get_text(strip=True)
                        if hero_text:
                            countered_by_list.append(hero_text)

                results.append({
                    "hero": hero_name,
                    "hero_cn": hero_name,
                    "hero_en": hero["english_name"],
                    "counters": counters_list,
                    "countered_by": countered_by_list,
                    "source_url": detail_url,
                })
            except Exception as e:
                logger.warning(f"抓取 {hero_name} 真实克制关系失败: {e}")

        logger.info("完成真实抓取，共获取 %d 个英雄的克制关系", len(results))
        return results

    def load_snapshot(self) -> Optional[Dict[str, Any]]:
        if not self.snapshot_path.exists():
            return None
        return json.loads(self.snapshot_path.read_text(encoding="utf-8"))

    def _is_stale(self, snapshot: Optional[Dict[str, Any]]) -> bool:
        if not snapshot or not snapshot.get("generated_at"):
            return True
        try:
            generated_at = datetime.fromisoformat(snapshot["generated_at"])
        except ValueError:
            return True
        return datetime.utcnow() - generated_at > timedelta(hours=settings.GAME_KNOWLEDGE_REFRESH_HOURS)

    def _build_documents(self, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        version_label = snapshot.get("version_label") or settings.GAME_DEFAULT_VERSION_LABEL
        documents: List[Dict[str, Any]] = []
        patch_notes = snapshot.get("patch_notes", {})

        summary = patch_notes.get("summary")
        if summary:
            documents.append({
                "id": f"patch-summary::{version_label}",
                "document": f"当前版本 {version_label} 的官方补丁摘要：{summary} 该信息来自王者荣耀官方补丁公告。",
                "metadata": {
                    "source_type": "patch_summary",
                    "version_label": version_label,
                    "source_url": patch_notes.get("url", ""),
                },
            })

        for idx, section in enumerate(patch_notes.get("sections", [])[:12], start=1):
            documents.append({
                "id": f"patch-section::{version_label}::{idx}",
                "document": f"版本 {version_label} 更新要点 {idx}：{section}",
                "metadata": {
                    "source_type": "patch_section",
                    "version_label": version_label,
                    "source_url": patch_notes.get("url", ""),
                },
            })

        for item in snapshot.get("win_rates", []):
            hero_name = item.get("hero_en") or item.get("hero")
            hero_cn = item.get("hero_cn") or hero_name
            text = (
                f"版本 {version_label} 的英雄胜率榜显示，{hero_name}（{hero_cn}）当前胜率为 {item.get('win_rate', '未知')}，"
                f"出场率为 {item.get('pick_rate') or '未知'}，禁用率为 {item.get('ban_rate') or '未知'}。"
            )
            if item.get("raw"):
                text += f" 榜单原始摘要：{item['raw']}。"
            documents.append({
                "id": f"winrate::{version_label}::{hero_name}",
                "document": text,
                "metadata": {
                    "source_type": "win_rate",
                    "version_label": version_label,
                    "hero": hero_name,
                    "hero_cn": hero_cn,
                    "source_url": item.get("source_url", self.WIN_RATE_URL),
                },
            })

        for item in snapshot.get("counters", []):
            hero_name = item.get("hero_en") or item.get("hero")
            hero_cn = item.get("hero_cn") or hero_name
            counters = "、".join(item.get("counters", [])) or "暂无"
            countered_by = "、".join(item.get("countered_by", [])) or "暂无"
            documents.append({
                "id": f"counter::{version_label}::{hero_name}",
                "document": f"版本 {version_label} 的克制关系中，{hero_name}（{hero_cn}）较擅长对抗 {counters}；同时更容易被 {countered_by} 压制。",
                "metadata": {
                    "source_type": "counter",
                    "version_label": version_label,
                    "hero": hero_name,
                    "hero_cn": hero_cn,
                    "source_url": item.get("source_url", self.WIN_RATE_URL),
                },
            })

        return documents

    def rebuild_index(self, snapshot: Dict[str, Any]) -> None:
        if chromadb is None:
            logger.warning("ChromaDB不可用，跳过索引重建")
            return

        docs = self._build_documents(snapshot)
        collection = self._get_collection(reset=True)
        if not docs:
            return

        texts = [item["document"] for item in docs]
        embeddings = self._embed_texts(texts)
        collection.add(
            ids=[item["id"] for item in docs],
            documents=texts,
            metadatas=[item["metadata"] for item in docs],
            embeddings=embeddings,
        )

    def refresh_knowledge_base(self) -> Dict[str, Any]:
        logger.info("开始刷新英雄版本知识库")
        previous = self.load_snapshot() or {}

        patch_notes = previous.get("patch_notes", {})
        champion_mappings = previous.get("champion_mappings", [])
        win_rates = previous.get("win_rates", [])
        counters = previous.get("counters", [])

        try:
            patch_meta = self._extract_patch_meta()
            patch_notes = self._extract_patch_notes(patch_meta)
        except Exception as exc:
            logger.warning("抓取补丁公告失败，继续使用旧数据：%s", exc)

        try:
            champion_mappings = self._fetch_champion_mappings()
        except Exception as exc:
            logger.warning("抓取英雄映射失败，继续使用旧数据：%s", exc)

        try:
            win_rates = self._fetch_win_rates(champion_mappings)
        except Exception as exc:
            logger.warning("抓取英雄胜率榜失败，继续使用旧数据：%s", exc)

        try:
            counters = self._fetch_counters(champion_mappings)
        except Exception as exc:
            logger.warning("抓取英雄克制关系失败，继续使用旧数据：%s", exc)

        version_label = (
            patch_notes.get("version_label")
            or previous.get("version_label")
            or settings.GAME_DEFAULT_VERSION_LABEL
        )

        snapshot = {
            "generated_at": datetime.utcnow().isoformat(),
            "version_label": version_label,
            "patch_notes": patch_notes,
            "champion_mappings": champion_mappings,
            "win_rates": win_rates,
            "counters": counters,
        }

        if not snapshot["patch_notes"] and not snapshot["win_rates"] and not snapshot["counters"]:
            raise RuntimeError("知识库刷新失败，未抓取到任何可用数据")

        self.snapshot_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.raw_dir / "latest_patch_notes.json").write_text(
            json.dumps(snapshot.get("patch_notes", {}), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.raw_dir / "latest_win_rates.json").write_text(
            json.dumps(snapshot.get("win_rates", []), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (self.raw_dir / "latest_counters.json").write_text(
            json.dumps(snapshot.get("counters", []), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.rebuild_index(snapshot)
        logger.info("知识库刷新完成，当前版本：%s", version_label)
        return snapshot

    def ensure_knowledge_base(self) -> Dict[str, Any]:
        snapshot = self.load_snapshot()
        if snapshot and not self._is_stale(snapshot):
            return snapshot

        if snapshot and not settings.GAME_KNOWLEDGE_AUTO_REFRESH:
            return snapshot

        try:
            return self.refresh_knowledge_base()
        except Exception as exc:
            logger.warning("自动刷新知识库失败：%s", exc)
            if snapshot:
                return snapshot
            return {
                "generated_at": datetime.utcnow().isoformat(),
                "version_label": settings.GAME_DEFAULT_VERSION_LABEL,
                "patch_notes": {},
                "champion_mappings": [],
                "win_rates": [],
                "counters": [],
            }

    @staticmethod
    def _dedupe(items) -> List[str]:
        seen = set()
        ordered: List[str] = []
        for item in items:
            if not item or item in seen:
                continue
            seen.add(item)
            ordered.append(item)
        return ordered

    def _extract_champions_from_text(
        self,
        text: str,
        champion_mappings: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not text:
            return []

        normalized_text = text.lower()
        matches: List[Dict[str, Any]] = []
        seen = set()

        for mapping in sorted(
            champion_mappings,
            key=lambda item: max((len(alias) for alias in item.get("aliases", []) or [""]), default=0),
            reverse=True,
        ):
            found = False
            for alias in mapping.get("aliases", []):
                alias = alias.strip()
                if not alias:
                    continue
                if re.search(r"[A-Za-z]", alias):
                    pattern = rf"(?<![a-z]){re.escape(alias.lower())}(?![a-z])"
                    found = re.search(pattern, normalized_text) is not None
                else:
                    found = alias in text
                if found:
                    key = mapping.get("english_name") or mapping.get("chinese_name")
                    if key and key not in seen:
                        seen.add(key)
                        matches.append(mapping)
                    break
        return matches

    def build_review_context(
        self,
        *,
        game_type: str,
        game_description: str,
        game_result: Optional[str] = None,
        kda: Optional[str] = None,
        team_composition: Optional[List[str]] = None,
        enemy_composition: Optional[List[str]] = None,
        game_version: Optional[str] = None,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        snapshot = self.ensure_knowledge_base()
        version_label = snapshot.get("version_label") or game_version or settings.GAME_DEFAULT_VERSION_LABEL
        champion_mappings = snapshot.get("champion_mappings", [])

        explicit_names = self._dedupe((team_composition or []) + (enemy_composition or []))
        explicit_mappings = self._extract_champions_from_text(" ".join(explicit_names), champion_mappings)
        detected_from_text = self._extract_champions_from_text(game_description, champion_mappings)
        detected = self._dedupe(
            [item.get("english_name") for item in explicit_mappings + detected_from_text if item.get("english_name")]
        )

        queries = [
            self._clean_text(
                " ".join(
                    filter(
                        None,
                        [
                            version_label,
                            game_type,
                            game_result or "",
                            kda or "",
                            " ".join(explicit_names),
                            game_description,
                            "当前强势英雄 弱势英雄 克制关系 阵容复盘",
                        ],
                    )
                )
            )
        ]
        for hero in detected[:4]:
            queries.append(f"{version_label} {hero} 当前版本胜率 克制关系 阵容强弱")

        collection = self._get_collection(reset=False)
        if collection is None:
            return {
                "version_label": version_label,
                "detected_champions": detected,
                "context_text": "ChromaDB不可用，无法检索知识库内容。",
                "retrieved_items": [],
            }

        try:
            collection_count = collection.count()
        except Exception:
            collection_count = 0

        if collection_count == 0:
            return {
                "version_label": version_label,
                "detected_champions": detected,
                "context_text": f"当前知识库中暂无 {version_label} 版本的可检索条目。",
                "retrieved_items": [],
            }

        hits: List[Dict[str, Any]] = []
        seen_ids = set()
        for query in queries:
            results = collection.query(
                query_embeddings=self._embed_texts([query]),
                n_results=min(3, collection_count),
            )
            ids = results.get("ids", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0] if results.get("distances") else []

            for index, doc_id in enumerate(ids):
                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)
                metadata = metadatas[index] if index < len(metadatas) else {}
                if metadata.get("version_label") and metadata.get("version_label") != version_label:
                    continue
                hits.append({
                    "id": doc_id,
                    "document": documents[index],
                    "metadata": metadata,
                    "distance": distances[index] if index < len(distances) else None,
                })
                if len(hits) >= top_k:
                    break
            if len(hits) >= top_k:
                break

        if not hits:
            context_text = f"当前知识库中暂无与该对局直接匹配的 {version_label} 版本信息。"
        else:
            lines = []
            for index, hit in enumerate(hits, start=1):
                source_type = hit["metadata"].get("source_type", "knowledge")
                source_url = hit["metadata"].get("source_url", "")
                lines.append(f"{index}. [{source_type}] {hit['document']} 来源：{source_url}")
            context_text = (
                f"当前知识库版本：{version_label}\n"
                f"识别到的相关英雄：{'、'.join(detected) if detected else '未从描述中稳定识别出英雄'}\n"
                f"检索命中的版本情报如下：\n" + "\n".join(lines)
            )

        return {
            "version_label": version_label,
            "detected_champions": detected,
            "context_text": context_text,
            "retrieved_items": hits,
        }


class LeagueOfLegendsKnowledgeService(BaseGameKnowledgeService):
    """英雄联盟真实知识库服务"""

    # 英雄联盟国服官方全英雄数据JSON接口
    LOL_HERO_API_URL = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"

    def __init__(self):
        super().__init__()
        self.game_name = "英雄联盟"
        self.game_code = "league_of_legends"
        self.collection_name = "lol_patch_knowledge"

    def _fetch_champion_mappings(self) -> List[Dict[str, Any]]:
        """从LOL官方接口抓取真实的英雄数据"""
        try:
            response = self.http.get(self.LOL_HERO_API_URL, timeout=10)
            data = response.json()
            heroes = data.get("hero", [])
            
            mappings = []
            for hero in heroes:
                hero_id = hero.get("heroId")
                en_name = hero.get("alias", "")       # 如: Annie
                cn_name = hero.get("name", "")        # 如: 安妮
                title = hero.get("title", "")         # 如: 黑暗之女
                roles = hero.get("roles", [])         # 如: ["mage"]
                
                mappings.append({
                    "champion_id": str(hero_id),
                    "english_name": en_name,
                    "chinese_name": cn_name,
                    "hero_title": title,
                    "roles": roles,
                    "aliases": [str(hero_id), cn_name, en_name, title],
                })
            logger.info("从LOL官方接口成功获取到 %d 个英雄数据", len(mappings))
            return mappings
        except Exception as e:
            logger.error("抓取LOL英雄数据失败: %s", e)
            return []

    def refresh_knowledge_base(self) -> Dict[str, Any]:
        """刷新英雄联盟知识库"""
        logger.info("开始刷新英雄联盟知识库")
        
        # 1. 抓取全英雄基础数据
        champion_mappings = self._fetch_champion_mappings()
        
        # 2. 生成基于官方定位的数据 (用于RAG向量检索)
        role_trans = {
            "fighter": "战士", "mage": "法师", "assassin": "刺客",
            "tank": "坦克", "marksman": "射手", "support": "辅助"
        }
        
        win_rates = []
        for hero in champion_mappings:
            roles_cn = [role_trans.get(r.lower(), r) for r in hero.get("roles", [])]
            roles_str = "、".join(roles_cn)
            win_rates.append({
                "hero": hero["chinese_name"],
                "hero_cn": hero["chinese_name"],
                "hero_en": hero["english_name"],
                "win_rate": "暂无", # 真实胜率需从OP.GG等第三方抓取，这里保留官方属性
                "raw": f"官方真实定位: 【{roles_str}】。英雄称号：{hero['hero_title']}。",
                "source_url": self.LOL_HERO_API_URL
            })

        snapshot = {
            "generated_at": datetime.utcnow().isoformat(),
            "version_label": "当前版本",
            "patch_notes": {},
            "champion_mappings": champion_mappings,
            "win_rates": win_rates,
            "counters": [], # 复杂克制关系建议让大模型自行推理，不灌输假数据
        }
        
        self.snapshot_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("英雄联盟知识库刷新完成")
        return snapshot

    def ensure_knowledge_base(self) -> Dict[str, Any]:
        snapshot = self.load_snapshot()
        if snapshot and not self._is_stale(snapshot):
            return snapshot
        return self.refresh_knowledge_base()

    def build_review_context(
        self,
        *,
        game_type: str,
        game_description: str,
        game_result: Optional[str] = None,
        kda: Optional[str] = None,
        team_composition: Optional[List[str]] = None,
        enemy_composition: Optional[List[str]] = None,
        game_version: Optional[str] = None,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """构建英雄联盟复盘上下文"""
        snapshot = self.ensure_knowledge_base()
        champion_mappings = snapshot.get("champion_mappings", [])
        
        # 使用基类的方法从文本中提取英雄名
        explicit_names = self._dedupe((team_composition or []) + (enemy_composition or []))
        detected_from_text = self._extract_champions_from_text(game_description, champion_mappings)
        detected = self._dedupe(
            [item.get("chinese_name") for item in detected_from_text if item.get("chinese_name")]
        )
        
        # 查找被识别出英雄的具体官方定位
        hero_details = []
        for d in detected:
            for mapping in champion_mappings:
                if mapping["chinese_name"] == d:
                    roles = mapping.get("roles", [])
                    hero_details.append(f"{mapping['chinese_name']}（{mapping['english_name']}，{mapping['hero_title']}）")
                    break

        context_text = (
            f"当前支持英雄联盟真实数据解析。\n"
            f"已从对局描述中识别到以下英雄：{'、'.join(hero_details) if hero_details else '未识别'}\n"
            f"请结合这些英雄的传统机制特性，对玩家的操作和阵容进行复盘。"
        )

        return {
            "version_label": "最新版本",
            "detected_champions": detected,
            "context_text": context_text,
            "retrieved_items": [],
        }


class GameKnowledgeManager:
    """游戏知识库管理器"""

    # 游戏类型映射
    GAME_TYPE_MAPPING = {
        "王者荣耀": "honor_kings",
        "honor_kings": "honor_kings",
        "王者荣耀手游": "honor_kings",
        "王者荣耀国际服": "honor_kings",
        "英雄联盟": "league_of_legends",
        "league_of_legends": "league_of_legends",
        "LOL": "league_of_legends",
        "lol": "league_of_legends",
        "英雄联盟手游": "league_of_legends",
        "金铲之战": "tactics",
        "云顶之弈": "tactics",
    }

    def __init__(self):
        self._services: Dict[str, BaseGameKnowledgeService] = {}
        self._initialize_services()

    def _initialize_services(self):
        """初始化所有游戏知识库服务"""
        self._services["honor_kings"] = HonorKingsKnowledgeService()
        self._services["league_of_legends"] = LeagueOfLegendsKnowledgeService()

        logger.info("游戏知识库管理器初始化完成，支持游戏：%s", list(self._services.keys()))

    def _normalize_game_type(self, game_type: str) -> str:
        """标准化游戏类型"""
        if not game_type:
            return "honor_kings"  # 默认王者荣耀

        normalized = game_type.strip().lower()
        return self.GAME_TYPE_MAPPING.get(normalized, "honor_kings")

    def get_service(self, game_type: str) -> BaseGameKnowledgeService:
        """根据游戏类型获取对应的知识库服务"""
        normalized_type = self._normalize_game_type(game_type)
        service = self._services.get(normalized_type)

        if not service:
            logger.warning("未知游戏类型 '%s'，使用默认服务（王者荣耀）", game_type)
            return self._services["honor_kings"]

        return service

    def get_supported_games(self) -> List[Dict[str, str]]:
        """获取支持的游戏列表"""
        return [
            {
                "code": code,
                "name": service.game_name if hasattr(service, "game_name") else code,
                "status": "已实现" if hasattr(service, "refresh_knowledge_base") else "未实现"
            }
            for code, service in self._services.items()
        ]

    def refresh_game_knowledge(self, game_type: str) -> Dict[str, Any]:
        """刷新指定游戏的知识库"""
        service = self.get_service(game_type)
        return service.refresh_knowledge_base()

    def build_context(
        self,
        game_type: str,
        game_description: str,
        game_result: Optional[str] = None,
        kda: Optional[str] = None,
        team_composition: Optional[List[str]] = None,
        enemy_composition: Optional[List[str]] = None,
        game_version: Optional[str] = None,
        top_k: int = 6,
    ) -> Dict[str, Any]:
        """构建指定游戏的复盘上下文"""
        service = self.get_service(game_type)
        return service.build_review_context(
            game_type=game_type,
            game_description=game_description,
            game_result=game_result,
            kda=kda,
            team_composition=team_composition,
            enemy_composition=enemy_composition,
            game_version=game_version,
            top_k=top_k,
        )


# 全局游戏知识库管理器实例
game_knowledge_manager = GameKnowledgeManager()


# 为了向后兼容，保留原有的全局实例
game_knowledge_service = game_knowledge_manager.get_service("王者荣耀")


# 导出原有服务的别名，保持向后兼容
__all__ = ['game_knowledge_manager', 'game_knowledge_service', 'GameKnowledgeManager']