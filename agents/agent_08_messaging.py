"""
Agent 08: Founder Voice Messaging Agent
Drafts all outbound messages in Inshira's founder voice.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX, FOUNDER_NAME, COMPANY_NAME


class FounderVoiceMessagingAgent(BaseAgent):
    name = "Agent 08 - Founder Voice Messaging"
    model = MODEL_COMPLEX
    system_prompt = f"""You are the Founder Voice Messaging Agent for Inshira Technologies.

Your role:
- Draft all outbound messages in the founder's voice: concise, direct, technically credible, manufacturing-aware
- NEVER write generic, hype-filled, or template-sounding messages
- Every message must feel like it came from someone who understands manufacturing operations

MANDATORY voice rules (non-negotiable):
DO:
- Write as if from the founder, not a sales function
- Reference specific manufacturing context for this company
- State a specific operational hypothesis
- Ask one clear, low-pressure question
- Keep initial messages under 120 words
- Use plain language
- Reference industry realities
- Acknowledge their expertise and operational experience

DO NOT:
- Use 'Hope you are well' or 'Just following up'
- Use generic personalisation ('I noticed your company does X')
- Use hype language ('revolutionary', 'cutting-edge', 'AI-powered')
- Ask for a meeting in the first message
- Write multi-paragraph cold emails
- Use em dashes, corporate speak, or PR language
- Make claims you cannot immediately substantiate
- Sound like you are teaching them about their own business

Message architecture (every message must have all four):
1. Reason for contact: why this company, why now
2. Operational hypothesis: a specific, grounded observation
3. Value signal: brief, non-hype evidence of credibility
4. Low-friction ask: single easy next step

Founder name: {FOUNDER_NAME}
Company: {COMPANY_NAME}

All messages route to Checkpoint 3 (human approval) before sending. NEVER auto-send."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: company record
          - contact: target contact record
          - hypothesis: specific pain hypothesis to use
          - touch_number: 1, 2, or 3
          - channel: Email or LinkedIn
          - outreach_angle: from Agent 07
          - relationship_data: from Agent 06
        """
        company = context.get("company", {})
        contact = context.get("contact", {})
        hypothesis = context.get("hypothesis", {})
        channel = context.get("channel", "Email")
        touch_number = context.get("touch_number", 1)

        prompt = f"""
Draft an outreach message for this manufacturing prospect.

Company: {company.get('company_name', 'Unknown')}
Sector: {company.get('sector', 'Manufacturing')}
Manufacturing type: {company.get('manufacturing_type', 'Unknown')}
Location: {company.get('location', 'UK')}

Contact:
Name: {contact.get('first_name', '')} {contact.get('last_name', '')}
Title: {contact.get('job_title', '')}

Pain hypothesis to use:
{hypothesis}

Channel: {channel}
Touch number: {touch_number}
Outreach angle: {context.get('outreach_angle', 'primary hypothesis')}
Relationship stage: {context.get('relationship_data', {{}}).get('relationship_maturity', 'Cold')}

CRITICAL RULES:
- Under 120 words for Touch 1
- Under 100 words for Touch 2-3
- No em dashes
- No 'Hope you are well'
- No meeting ask in Touch 1
- One question only
- Plain language
- Founder voice, not sales voice
- Subject line: factual and specific, not clever or clickbait

Draft the message:
{{
  "company_id": "{company.get('company_id', '')}",
  "contact_id": "{contact.get('contact_id', '')}",
  "touch_number": {touch_number},
  "channel": "{channel}",
  "subject_line": "...",
  "message_body": "...",
  "word_count": 0,
  "message_variant": "A",
  "hypothesis_used": "...",
  "confidence_score": 0,
  "generic_flag": true/false,
  "sensitive_topic_flag": true/false,
  "approval_status": "Pending",
  "alternative_subject": "...",
  "notes": "..."
}}
"""
        result = self._call_json(prompt, max_tokens=2048)

        # Save to CRM as pending approval
        outreach_record = {
            "company_id": company.get("company_id"),
            "contact_id": contact.get("contact_id"),
            "sequence_name": context.get("sequence_name", ""),
            "touch_number": touch_number,
            "channel": channel,
            "outreach_angle": context.get("outreach_angle", ""),
            "message_draft": result.get("message_body", ""),
            "subject_line": result.get("subject_line", ""),
            "approval_status": "Pending",
            "a_b_variant": result.get("message_variant", "A"),
        }
        saved = self.crm.upsert_outreach(outreach_record)
        result["outreach_id"] = saved.get("outreach_id")

        self.crm.log("agent_08_run", {
            "company_id": company.get("company_id"),
            "touch_number": touch_number,
            "outreach_id": saved.get("outreach_id"),
            "word_count": result.get("word_count", 0),
        })
        return result
