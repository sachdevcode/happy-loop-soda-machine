import instructor
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
import os
import re
from enum import Enum


api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")


client = None
if api_key and api_key != "dummy-key-for-testing":
    try:
        client = instructor.from_provider(
            "openai/gpt-3.5-turbo",
            api_key=api_key,
            base_url=base_url
        )
    except Exception:
        client = None

class IntentType(str, Enum):
    """Enum for different types of user intents"""
    PURCHASE = "purchase"
    QUERY = "query"
    CANCEL = "cancel"
    REFUSE = "refuse"
    UNKNOWN = "unknown"

class PurchaseIntent(BaseModel):
    """Parsed purchase intent from natural language with enhanced validation"""
    intent: IntentType = Field(description="The user's intent: purchase, query, cancel, refuse, or unknown")
    product_name: Optional[str] = Field(default=None, description="Name of the product to purchase")
    quantity: Optional[int] = Field(default=None, description="Quantity to purchase")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for the parsing (0-1)")
    reasoning: str = Field(description="Brief explanation of why this intent was chosen")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence must be between 0 and 1')
        return v
    
    @classmethod
    def from_message(cls, message: str, available_products: List[str]) -> "PurchaseIntent":
        """Parse natural language message into purchase intent with enhanced logic"""
        
        if client is not None:
            return cls._ai_parse(message, available_products)
        else:
            return cls._enhanced_fallback_parse(message, available_products)
    
    @classmethod
    def _ai_parse(cls, message: str, available_products: List[str]) -> "PurchaseIntent":
        """AI-powered parsing using Instructor"""
        system_prompt = f"""
        You are an AI assistant for a soda vending machine. 
        Parse the user's message and extract their intent with high accuracy.
        
        Available products: {', '.join(available_products)}
        
        Rules:
        1. INTENT DETECTION:
           - "purchase": User wants to buy something (positive intent)
           - "query": User is asking about products/inventory
           - "cancel": User wants to cancel a transaction
           - "refuse": User explicitly says no/doesn't want to buy
           - "unknown": Intent is unclear
        
        2. PRODUCT EXTRACTION:
           - Must match one of the available products exactly
           - Handle variations (coke/coca-cola, sprite/lemon-lime)
        
        3. QUANTITY EXTRACTION:
           - Extract numbers followed by product names
           - Default to 1 if not specified
           - Handle "a", "an", "one" as quantity 1
        
        4. CONFIDENCE SCORING:
           - 0.9-1.0: Very clear intent
           - 0.7-0.8: Clear intent with some ambiguity
           - 0.5-0.6: Somewhat clear
           - 0.3-0.4: Unclear
           - 0.1-0.2: Very unclear
        
        Examples:
        - "I want to buy 3 cokes" → purchase, coke, 3, 0.95
        - "Give me a sprite" → purchase, sprite, 1, 0.9
        - "What do you have?" → query, null, null, 0.95
        - "I don't want to buy anything" → refuse, null, null, 0.9
        - "Cancel my order" → cancel, null, null, 0.9
        """
        
        try:
            response = client.chat.completions.create(
                response_model=PurchaseIntent,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_retries=3
            )
            return response
        except Exception as e:
            
            return cls._enhanced_fallback_parse(message, available_products)
    
    @classmethod
    def _enhanced_fallback_parse(cls, message: str, available_products: List[str]) -> "PurchaseIntent":
        """Enhanced fallback parser with better intent detection"""
        message_lower = message.lower().strip()
        
       
        negative_patterns = [
            r'\b(?:dont|don\'t|not|no|never|refuse|decline|cancel|stop)\b',
            r'\b(?:dont|don\'t)\s+(?:want|need|buy|purchase)\b',
            r'\b(?:not|no)\s+(?:thanks|thank you|interested)\b'
        ]
        
        has_negative = any(re.search(pattern, message_lower) for pattern in negative_patterns)
        
        
        purchase_patterns = [
            r'\b(?:buy|purchase|get|want|need)\b',
            r'\b(?:give me|i\'ll take|i want)\b',
            r'\b(?:can i have|may i have)\b'
        ]
        
        has_purchase_keyword = any(re.search(pattern, message_lower) for pattern in purchase_patterns)
        
        
        query_patterns = [
            r'\b(?:what|which|how many|show me|list|available)\b',
            r'\b(?:do you have|what\'s available)\b',
            r'\b(?:inventory|stock|products)\b'
        ]
        
        has_query_keyword = any(re.search(pattern, message_lower) for pattern in query_patterns)
        
        
        cancel_patterns = [
            r'\b(?:cancel|stop|abort|undo)\b',
            r'\b(?:never mind|forget it)\b'
        ]
        
        has_cancel_keyword = any(re.search(pattern, message_lower) for pattern in cancel_patterns)
        
        
        if has_negative and has_purchase_keyword:
            return cls(
                intent=IntentType.REFUSE,
                product_name=None,
                quantity=None,
                confidence=0.9,
                reasoning="User expressed negative intent with purchase keywords"
            )
        elif has_cancel_keyword:
            return cls(
                intent=IntentType.CANCEL,
                product_name=None,
                quantity=None,
                confidence=0.8,
                reasoning="User used cancel/stop keywords"
            )
        elif has_query_keyword:
            return cls(
                intent=IntentType.QUERY,
                product_name=None,
                quantity=None,
                confidence=0.85,
                reasoning="User asked about inventory/products"
            )
        elif has_purchase_keyword and not has_negative:
            
            product_name = cls._extract_product(message_lower, available_products)
            quantity = cls._extract_quantity(message_lower)
            
            confidence = 0.7 if product_name else 0.3
            
            return cls(
                intent=IntentType.PURCHASE,
                product_name=product_name,
                quantity=quantity,
                confidence=confidence,
                reasoning=f"Purchase intent detected. Product: {product_name}, Quantity: {quantity}"
            )
        else:
            return cls(
                intent=IntentType.UNKNOWN,
                product_name=None,
                quantity=None,
                confidence=0.5,
                reasoning="Intent unclear - no clear purchase, query, or cancel keywords"
            )
    
    @staticmethod
    def _extract_product(message: str, available_products: List[str]) -> Optional[str]:
        """Extract product name from message"""
        for product in available_products:
            if product in message:
                return product
        return None
    
    @staticmethod
    def _extract_quantity(message: str) -> int:
        """Extract quantity from message"""
        
        quantity_patterns = [
            r'(\d+)\s*(?:cans?|bottles?|sodas?|cokes?|pepsis?|sprites?|fantas?|mountain\s*dews?|dr\s*peppers?)',
            r'(?:buy|get|want|need)\s+(\d+)',
            r'(\d+)\s+(?:coke|pepsi|sprite|fanta|mountain\s*dew|dr\s*pepper)'
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, message)
            if match:
                return int(match.group(1))
        
        
        if re.search(r'\b(?:a|an)\s+(?:coke|pepsi|sprite|fanta|mountain\s*dew|dr\s*pepper)', message):
            return 1
        
        return 1  

def parse_purchase_request(message: str, available_products: List[str]) -> PurchaseIntent:
    """Parse a natural language purchase request with enhanced validation"""
    return PurchaseIntent.from_message(message, available_products) 