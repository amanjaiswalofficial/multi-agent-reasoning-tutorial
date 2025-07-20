import re
from schemas.decision import ArticleDecision, DebateResponse, ReasoningStep
from models.model_manager import SimpleOllamaAgent

def parse_decision(text: str, agent_name: str) -> ArticleDecision:
    """Parse decision from text response"""
    # Extract action
    action = "skip"  # default
    if "summarize" in text.lower():
        action = "summarize"
    elif "save_for_later" in text.lower() or "save for later" in text.lower():
        action = "save_for_later"
    
    # Extract reason (first sentence or paragraph)
    lines = text.strip().split('\n')
    reason = lines[0] if lines else "No reason provided"
    
    # Extract confidence (look for numbers between 0 and 1)
    confidence_match = re.search(r'confidence[:\s]*([0-9]*\.?[0-9]+)', text.lower())
    confidence = float(confidence_match.group(1)) if confidence_match else 0.7
    confidence = min(max(confidence, 0.0), 1.0)  # Clamp to 0-1
    
    # Create simple reasoning chain
    reasoning_chain = [
        ReasoningStep(
            step="Content Analysis",
            analysis=f"Analyzed article content and applied {agent_name} preferences",
            confidence=confidence
        )
    ]
    
    # Extract key factors
    key_factors = ["content_quality", "length", "relevance"]
    
    return ArticleDecision(
        action=action,
        reason=reason,
        reasoning_chain=reasoning_chain,
        confidence=confidence,
        key_factors=key_factors
    )

def create_decision_agent(agent_name: str, system_prompt: str):
    agent = SimpleOllamaAgent()
    
    async def run(article):
        prompt = f"""
        You are {agent_name}. {system_prompt}
        
        Analyze this article:
        Title: {article.title}
        Word Count: {article.word_count}
        Content: {article.content[:1000]}...
        
        Based on your preferences, decide:
        - "summarize" if you want to create a summary
        - "skip" if you want to skip this article
        - "save_for_later" if you want to read it later
        
        Provide your decision and reasoning. Include a confidence score (0.0 to 1.0).
        
        Decision:
        """
        
        system = f"You are {agent_name}, an AI agent that analyzes articles. Be concise and decisive."
        
        response = await agent.generate(prompt, system)
        return parse_decision(response, agent_name)
    
    async def debate(article, other_decisions, round_num=1):
        # Simplified debate - just return a basic response
        return DebateResponse(
            agent_name=agent_name,
            response_to="other_agents",
            argument=f"I maintain my position based on {agent_name} principles",
            counter_points=["different_priorities"],
            final_stance=await run(article)  # Re-run decision
        )
    
    return run, debate

PERSONAS = {
    "SpeedReader": "You prefer short, scannable articles. You value efficiency and quick insights. You skip long-form content unless it's exceptionally valuable.",
    "DepthSeeker": "You love long-form, technical content. You prioritize comprehensive analysis and detailed explanations. You skip superficial content.",
    "FreshnessAgent": "You prioritize recent or trending posts. You value timely information and breaking news. You skip outdated content unless it's timeless."
}
