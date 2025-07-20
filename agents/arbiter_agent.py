from schemas.decision import ArticleDecision, DebateResponse, ReasoningStep
from models.model_manager import SimpleOllamaAgent


def parse_arbiter_decision(text: str) -> ArticleDecision:
    """Parse arbiter decision from text response"""
    # Extract action
    action = "skip"  # default
    if "summarize" in text.lower():
        action = "summarize"
    elif "save_for_later" in text.lower() or "save for later" in text.lower():
        action = "save_for_later"
    
    # Extract reason
    lines = text.strip().split('\n')
    reason = lines[0] if lines else "Arbiter decision based on agent consensus"
    
    # Default confidence
    confidence = 0.8
    
    # Create reasoning chain
    reasoning_chain = [
        ReasoningStep(
            step="Agent Analysis",
            analysis="Analyzed all agent decisions and reasoning",
            confidence=0.8
        ),
        ReasoningStep(
            step="Final Decision",
            analysis="Made final decision based on strongest arguments",
            confidence=0.8
        )
    ]
    
    key_factors = ["agent_consensus", "reasoning_quality", "confidence_levels"]
    
    return ArticleDecision(
        action=action,
        reason=reason,
        reasoning_chain=reasoning_chain,
        confidence=confidence,
        key_factors=key_factors
    )

def create_arbiter_agent():
    agent = SimpleOllamaAgent()
    
    async def run(article, votes, debate_responses=None):
        votes_summary = "\n".join([
            f"- {name}: {vote.action} (confidence: {vote.confidence}) - {vote.reason}"
            for name, vote in votes
        ])
        
        prompt = f"""
        You are an arbiter making the final decision about this article:
        
        Title: {article.title}
        Word Count: {article.word_count}
        
        Agent Decisions:
        {votes_summary}
        
        Based on the agent decisions and reasoning, make the final choice:
        - "summarize" to create a summary
        - "skip" to skip this article
        - "save_for_later" to save for later
        
        Consider the quality of reasoning and confidence levels.
        
        Final Decision:
        """
        
        system = "You are a fair arbiter. Make decisions based on the strongest evidence and reasoning from the agents."
        
        response = await agent.generate(prompt, system)
        return parse_arbiter_decision(response)
    
    return run
