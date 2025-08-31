"""
YouTube Comment Scraper Service
Advanced YouTube comment collection with rate limiting and brand detection
"""
import asyncio
import re
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import aiohttp
from youtube_comment_downloader import YoutubeCommentDownloader
import logging
from ..core.config import settings, EV_BRANDS
from ..models.comment import Comment, CommentCreate, CommentSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeScraper:
    def __init__(self):
        self.downloader = YoutubeCommentDownloader()
        self.rate_limit_delay = 3600 / settings.youtube_rate_limit  # seconds between requests
        self.last_request_time = None
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the scraper with aiohttp session"""
        self.session = aiohttp.ClientSession()
        logger.info("✅ YouTube Scraper initialized")
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit_wait(self):
        """Implement rate limiting"""
        if self.last_request_time:
            elapsed = datetime.now().timestamp() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - elapsed
                logger.info(f"⏳ Rate limiting: waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        self.last_request_time = datetime.now().timestamp()
    
    def _detect_brand_mentions(self, text: str) -> Dict[str, List[str]]:
        """Detect EV brand mentions in comment text"""
        mentions = {}
        text_lower = text.lower()
        
        for brand_id, brand_info in EV_BRANDS.items():
            found_keywords = []
            
            # Check main keywords
            for keyword in brand_info["keywords"]:
                if keyword.lower() in text_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                mentions[brand_id] = found_keywords
        
        return mentions
    
    def _clean_comment_text(self, text: str) -> str:
        """Clean and normalize comment text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove some common spam patterns
        text = re.sub(r'[👆☝️⬆️↗️↖️⬆⬇️➡️⬅️]{2,}', '', text)  # Remove excessive arrows
        text = re.sub(r'[��💯🚀⚡]{3,}', '', text)  # Remove excessive emojis
        
        return text
    
    def _is_spam_comment(self, comment_data: Dict) -> bool:
        """Basic spam detection"""
        text = comment_data.get('text', '').lower()
        author = comment_data.get('author', '').lower()
        
        # Spam indicators
        spam_patterns = [
            r'click here',
            r'subscribe.{0,20}channel',
            r'check.{0,10}bio',
            r'dm.{0,10}me',
            r'whatsapp.{0,10}\+?\d+',
            r'telegram.{0,10}@',
            r'👆.{0,20}👆',
            r'free.{0,20}money',
            r'earn.{0,20}₹'
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, text):
                return True
        
        # Check for bot-like usernames
        if re.search(r'\d{4,}$', author) or len(author) < 3:
            return True
        
        return False
    
    def _is_bot_account(self, comment_data: Dict) -> bool:
        """Detect potential bot accounts"""
        author = comment_data.get('author', '')
        
        # Bot indicators
        bot_patterns = [
            r'^[a-zA-Z]+\d{4,}$',  # Letters followed by many numbers
            r'^User\d+$',           # Generic User123 pattern
            r'bot|spam|fake',       # Contains bot-related words
        ]
        
        for pattern in bot_patterns:
            if re.search(pattern, author, re.IGNORECASE):
                return True
        
        return False
    
    async def search_videos_by_keywords(self, keywords: List[str], max_results: int = 10) -> List[Dict]:
        """Search for YouTube videos using keywords"""
        await self._rate_limit_wait()
        
        # This would typically use YouTube Data API
        # For now, returning mock data structure
        videos = []
        
        for keyword in keywords[:3]:  # Limit to avoid rate limiting
            search_results = await self._mock_youtube_search(keyword, max_results // len(keywords))
            videos.extend(search_results)
        
        return videos
    
    async def _mock_youtube_search(self, keyword: str, max_results: int) -> List[Dict]:
        """Mock YouTube search - replace with actual YouTube Data API"""
        # This is a placeholder - implement actual YouTube Data API integration
        mock_videos = [
            {
                "video_id": f"mock_{keyword}_{i}",
                "title": f"Video about {keyword} - Review {i}",
                "channel": f"Channel{i}",
                "published_at": datetime.now() - timedelta(days=i),
                "view_count": 10000 + i * 1000,
                "comment_count": 100 + i * 10
            }
            for i in range(min(max_results, 3))
        ]
        
        return mock_videos
    
    async def scrape_video_comments(self, video_id: str, max_comments: int = None) -> List[CommentCreate]:
        """Scrape comments from a specific YouTube video"""
        await self._rate_limit_wait()
        
        if max_comments is None:
            max_comments = settings.max_comments_per_video
        
        comments = []
        
        try:
            logger.info(f"🎥 Scraping comments from video: {video_id}")
            
            # Use youtube-comment-downloader
            comment_generator = self.downloader.get_comments_from_url(
                f"https://www.youtube.com/watch?v={video_id}",
                sort_by=1  # Sort by top comments
            )
            
            for i, comment_data in enumerate(comment_generator):
                if i >= max_comments:
                    break
                
                # Clean and validate comment
                text = self._clean_comment_text(comment_data.get('text', ''))
                if len(text) < 10:  # Skip very short comments
                    continue
                
                # Detect brand mentions
                brand_mentions = self._detect_brand_mentions(text)
                if not brand_mentions:  # Skip comments without EV brand mentions
                    continue
                
                # Get the primary brand mentioned
                primary_brand = list(brand_mentions.keys())[0]
                
                # Create comment object
                comment = CommentCreate(
                    text=text,
                    source=CommentSource.YOUTUBE,
                    source_id=comment_data.get('cid', ''),
                    source_url=f"https://www.youtube.com/watch?v={video_id}",
                    video_id=video_id,
                    author_name=comment_data.get('author', 'Unknown'),
                    author_id=comment_data.get('author_id'),
                    likes_count=comment_data.get('votes', 0),
                    replies_count=comment_data.get('replies', 0),
                    published_at=datetime.fromisoformat(comment_data.get('time', datetime.now().isoformat())),
                    metadata={
                        'brand_mentions': brand_mentions,
                        'primary_brand': primary_brand,
                        'brand_keywords': brand_mentions[primary_brand],
                        'is_spam': self._is_spam_comment(comment_data),
                        'is_bot': self._is_bot_account(comment_data),
                        'reply_count': comment_data.get('replies', 0),
                        'raw_data': comment_data
                    }
                )
                
                comments.append(comment)
                
                if len(comments) % 10 == 0:
                    logger.info(f"📝 Scraped {len(comments)} EV-related comments so far...")
            
            logger.info(f"✅ Scraped {len(comments)} EV-related comments from video {video_id}")
            
        except Exception as e:
            logger.error(f"❌ Error scraping video {video_id}: {str(e)}")
        
        return comments
    
    async def scrape_brand_comments(self, brand_id: str, max_videos: int = 5, max_comments_per_video: int = 100) -> List[CommentCreate]:
        """Scrape comments for a specific EV brand"""
        if brand_id not in EV_BRANDS:
            raise ValueError(f"Unknown brand: {brand_id}")
        
        brand_info = EV_BRANDS[brand_id]
        keywords = brand_info["keywords"]
        
        logger.info(f"🔍 Starting comment scraping for {brand_info['name']}")
        
        # Search for videos
        videos = await self.search_videos_by_keywords(keywords, max_videos)
        
        all_comments = []
        
        for video in videos:
            video_comments = await self.scrape_video_comments(
                video["video_id"], 
                max_comments_per_video
            )
            all_comments.extend(video_comments)
            
            # Add delay between videos
            await asyncio.sleep(2)
        
        logger.info(f"✅ Total comments scraped for {brand_info['name']}: {len(all_comments)}")
        return all_comments
    
    async def scrape_all_brands(self, max_videos_per_brand: int = 3) -> Dict[str, List[CommentCreate]]:
        """Scrape comments for all EV brands"""
        logger.info(f"🚀 Starting comprehensive scraping for all {len(EV_BRANDS)} EV brands")
        
        results = {}
        
        for brand_id in EV_BRANDS.keys():
            try:
                brand_comments = await self.scrape_brand_comments(
                    brand_id, 
                    max_videos_per_brand, 
                    50  # Reduced per video to avoid overwhelming
                )
                results[brand_id] = brand_comments
                
                # Longer delay between brands
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Failed to scrape {brand_id}: {str(e)}")
                results[brand_id] = []
        
        total_comments = sum(len(comments) for comments in results.values())
        logger.info(f"🎉 Scraping complete! Total comments: {total_comments}")
        
        return results

# Usage example and testing
async def test_scraper():
    scraper = YouTubeScraper()
    await scraper.initialize()
    
    try:
        # Test scraping for one brand
        ola_comments = await scraper.scrape_brand_comments("ola_electric", max_videos=2, max_comments_per_video=20)
        print(f"Scraped {len(ola_comments)} comments for Ola Electric")
        
        # Print first comment as example
        if ola_comments:
            print(f"Example comment: {ola_comments[0].text[:100]}...")
            
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_scraper())
