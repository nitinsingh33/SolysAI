"""
Sentiment Analysis Service
AI-powered sentiment analysis using OpenAI and Gemini APIs
"""
import asyncio
import openai
import google.generativeai as genai
from typing import List, Dict, Optional, Any
import logging
import json
import re
from datetime import datetime
from ..core.config import settings
from ..models.sentiment import (
    SentimentAnalysis, SentimentCreate, SentimentLabel, 
    EmotionLabel, AnalysisMethod, EV_ASPECTS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.openai_client = None
        self.gemini_model = None
        self.initialize_apis()
    
    def initialize_apis(self):
        """Initialize AI API clients"""
        try:
            # Initialize OpenAI
            if settings.openai_api_key:
                openai.api_key = settings.openai_api_key
                self.openai_client = openai
                logger.info("✅ OpenAI client initialized")
            
            # Initialize Gemini
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini client initialized")
                
        except Exception as e:
            logger.error(f"❌ Error initializing AI APIs: {str(e)}")
    
    def _extract_aspects_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract EV-specific aspects mentioned in the text"""
        text_lower = text.lower()
        found_aspects = {}
        
        for aspect, keywords in EV_ASPECTS.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                found_aspects[aspect] = found_keywords
        
        return found_aspects
    
    def _detect_comparison(self, text: str) -> Dict[str, Any]:
        """Detect if the comment mentions comparison with other brands"""
        comparison_patterns = [
            r'better than',
            r'worse than', 
            r'compared to',
            r'vs\s+',
            r'versus',
            r'rather than',
            r'instead of'
        ]
        
        text_lower = text.lower()
        has_comparison = any(re.search(pattern, text_lower) for pattern in comparison_patterns)
        
        # Extract mentioned brands (simplified)
        from ..core.config import EV_BRANDS
        mentioned_brands = []
        for brand_id, brand_info in EV_BRANDS.items():
            for keyword in brand_info["keywords"]:
                if keyword.lower() in text_lower:
                    mentioned_brands.append(brand_id)
        
        return {
            "has_comparison": has_comparison,
            "mentioned_brands": list(set(mentioned_brands)),
            "comparison_count": len(set(mentioned_brands))
        }
    
    def _detect_sarcasm(self, text: str, sentiment_score: float) -> bool:
        """Basic sarcasm detection"""
        sarcasm_indicators = [
            r'oh\s+great',
            r'just\s+perfect',
            r'wonderful',
            r'fantastic.*problem',
            r'love.*when.*fail',
            r'amazing.*not.*work'
        ]
        
        text_lower = text.lower()
        
        # Check for sarcasm patterns
        has_sarcasm_pattern = any(re.search(pattern, text_lower) for pattern in sarcasm_indicators)
        
        # Check for contradiction (positive words with negative sentiment)
        positive_words = ['great', 'amazing', 'perfect', 'wonderful', 'fantastic', 'love']
        has_positive_words = any(word in text_lower for word in positive_words)
        
        # If text has positive words but negative sentiment, might be sarcasm
        contradiction_sarcasm = has_positive_words and sentiment_score < -0.3
        
        return has_sarcasm_pattern or contradiction_sarcasm
    
    async def analyze_with_openai(self, text: str, brand: str) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI"""
        if not self.openai_client or not settings.openai_api_key:
            raise ValueError("OpenAI not configured")
        
        prompt = f"""
        Analyze the sentiment of this comment about the EV brand "{brand}":
        
        Comment: "{text}"
        
        Provide a JSON response with:
        1. sentiment_label: "positive", "negative", "neutral", or "mixed"
        2. sentiment_score: float from -1.0 (very negative) to 1.0 (very positive)
        3. confidence_score: float from 0.0 to 1.0
        4. brand_sentiment: specific sentiment toward the brand (-1.0 to 1.0)
        5. emotions: object with emotion scores (joy, anger, fear, sadness, surprise, disgust, trust, anticipation)
        6. dominant_emotion: the strongest emotion
        7. aspects: object analyzing sentiment for battery, performance, design, build_quality, features, service, price, charging_infrastructure
        8. keywords_positive: array of positive keywords found
        9. keywords_negative: array of negative keywords found
        10. themes: array of main themes discussed
        11. sarcasm_detected: boolean
        
        Focus on Indian EV context and be precise with sentiment scoring.
        """
        
        try:
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing sentiment in Indian electric vehicle discussions. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            raise
    
    async def analyze_with_gemini(self, text: str, brand: str) -> Dict[str, Any]:
        """Analyze sentiment using Gemini"""
        if not self.gemini_model:
            raise ValueError("Gemini not configured")
        
        prompt = f"""
        Analyze the sentiment of this comment about the EV brand "{brand}":
        
        Comment: "{text}"
        
        Return JSON with sentiment_label, sentiment_score (-1 to 1), confidence_score (0 to 1), 
        brand_sentiment, emotions, dominant_emotion, aspects analysis for EV features,
        keywords_positive, keywords_negative, themes, and sarcasm_detected.
        
        Focus on Indian electric vehicle context.
        """
        
        try:
            response = await self.gemini_model.generate_content_async(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                raise ValueError("No valid JSON found in Gemini response")
                
        except Exception as e:
            logger.error(f"Gemini analysis failed: {str(e)}")
            raise
    
    def _fallback_analysis(self, text: str, brand: str) -> Dict[str, Any]:
        """Fallback rule-based sentiment analysis"""
        logger.info("Using fallback rule-based analysis")
        
        text_lower = text.lower()
        
        # Simple keyword-based sentiment
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'fantastic', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'useless', 'problem', 'issue']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment_label = "positive"
            sentiment_score = 0.6
        elif negative_count > positive_count:
            sentiment_label = "negative"
            sentiment_score = -0.6
        else:
            sentiment_label = "neutral"
            sentiment_score = 0.0
        
        return {
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "confidence_score": 0.5,  # Low confidence for fallback
            "brand_sentiment": sentiment_score,
            "emotions": {"neutral": 1.0},
            "dominant_emotion": "neutral",
            "aspects": {},
            "keywords_positive": [word for word in positive_words if word in text_lower],
            "keywords_negative": [word for word in negative_words if word in text_lower],
            "themes": ["general"],
            "sarcasm_detected": False
        }
    
    async def analyze_single_comment(
        self, 
        comment_text: str, 
        brand: str,
        method: AnalysisMethod = AnalysisMethod.OPENAI
    ) -> SentimentAnalysis:
        """Analyze sentiment for a single comment"""
        
        start_time = datetime.now()
        
        try:
            # Choose analysis method
            if method == AnalysisMethod.OPENAI:
                analysis_result = await self.analyze_with_openai(comment_text, brand)
            elif method == AnalysisMethod.GEMINI:
                analysis_result = await self.analyze_with_gemini(comment_text, brand)
            else:
                analysis_result = self._fallback_analysis(comment_text, brand)
            
            # Additional processing
            comparison_info = self._detect_comparison(comment_text)
            aspects_found = self._extract_aspects_from_text(comment_text)
            
            # Calculate processing time
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Create sentiment analysis object
            sentiment_analysis = SentimentAnalysis(
                comment_text=comment_text,
                sentiment_label=SentimentLabel(analysis_result["sentiment_label"]),
                sentiment_score=analysis_result["sentiment_score"],
                confidence_score=analysis_result["confidence_score"],
                brand_mentioned=brand,
                brand_sentiment=analysis_result["brand_sentiment"],
                emotions={EmotionLabel(k): v for k, v in analysis_result.get("emotions", {}).items() if k in EmotionLabel.__members__},
                dominant_emotion=EmotionLabel(analysis_result.get("dominant_emotion", "neutral")) if analysis_result.get("dominant_emotion") in EmotionLabel.__members__ else None,
                aspects=analysis_result.get("aspects", {}),
                analysis_method=method,
                processing_time_ms=processing_time,
                sarcasm_detected=analysis_result.get("sarcasm_detected", False),
                comparison_mentioned=comparison_info["has_comparison"],
                compared_brands=comparison_info["mentioned_brands"],
                keywords_positive=analysis_result.get("keywords_positive", []),
                keywords_negative=analysis_result.get("keywords_negative", []),
                themes=analysis_result.get("themes", [])
            )
            
            return sentiment_analysis
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed for comment: {str(e)}")
            
            # Return fallback analysis on error
            fallback_result = self._fallback_analysis(comment_text, brand)
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return SentimentAnalysis(
                comment_text=comment_text,
                sentiment_label=SentimentLabel(fallback_result["sentiment_label"]),
                sentiment_score=fallback_result["sentiment_score"],
                confidence_score=fallback_result["confidence_score"],
                brand_mentioned=brand,
                brand_sentiment=fallback_result["brand_sentiment"],
                analysis_method=AnalysisMethod.RULE_BASED,
                processing_time_ms=processing_time
            )
    
    async def analyze_batch(
        self, 
        comments: List[Dict[str, str]], 
        method: AnalysisMethod = AnalysisMethod.OPENAI
    ) -> List[SentimentAnalysis]:
        """Analyze sentiment for multiple comments"""
        
        logger.info(f"🔍 Starting batch analysis of {len(comments)} comments using {method}")
        
        results = []
        batch_size = settings.batch_size
        
        for i in range(0, len(comments), batch_size):
            batch = comments[i:i + batch_size]
            
            # Process batch
            batch_tasks = [
                self.analyze_single_comment(
                    comment["text"], 
                    comment["brand"], 
                    method
                ) 
                for comment in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [r for r in batch_results if isinstance(r, SentimentAnalysis)]
            results.extend(valid_results)
            
            logger.info(f"✅ Processed batch {i//batch_size + 1}/{(len(comments)-1)//batch_size + 1}")
            
            # Add delay between batches to respect rate limits
            if i + batch_size < len(comments):
                await asyncio.sleep(1)
        
        logger.info(f"🎉 Batch analysis complete! Processed {len(results)}/{len(comments)} comments")
        return results

# Usage example
async def test_sentiment_analyzer():
    analyzer = SentimentAnalyzer()
    
    # Test single comment
    comment = "I love my Ola S1 Pro! Amazing battery life and smooth ride. Best EV in India!"
    result = await analyzer.analyze_single_comment(comment, "ola_electric")
    
    print(f"Sentiment: {result.sentiment_label}")
    print(f"Score: {result.sentiment_score}")
    print(f"Confidence: {result.confidence_score}")
    print(f"Keywords: {result.keywords_positive}")

if __name__ == "__main__":
    asyncio.run(test_sentiment_analyzer())
