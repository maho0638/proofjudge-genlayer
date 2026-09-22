# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class Review:
    id: str
    creator: Address
    requirement: str
    evidence_url: str
    status: str
    confidence: u256
    summary: str


class ProofJudge(gl.Contract):
    reviews: TreeMap[str, Review]

    def __init__(self):
        pass

    def _evaluate(self, requirement: str, evidence_url: str) -> dict:
        def evaluate_once() -> str:
            evidence = gl.nondet.web.render(evidence_url, mode="text")
            task = f"""
You are evaluating evidence for a task completion claim.

REQUIREMENT:
{requirement}

EVIDENCE FROM URL:
{evidence}

Return JSON only in exactly this shape:
{{
  "approved": bool,
  "confidence": int,
  "summary": str
}}

Rules:
- approved is true only if the evidence clearly satisfies the requirement.
- confidence must be an integer from 0 to 100.
- summary must be concise, factual, and under 240 characters.
- if evidence is missing, ambiguous, or unrelated, approved must be false.
- output JSON only, with no markdown or extra text.
"""
            result = gl.nondet.exec_prompt(task, response_format="json")
            return json.dumps(result, sort_keys=True)

        return json.loads(gl.eq_principle.strict_eq(evaluate_once))

    @gl.public.write
    def submit_review(
        self, review_id: str, requirement: str, evidence_url: str
    ) -> None:
        if not review_id or not requirement or not evidence_url:
            raise Exception("Missing required field")

        if review_id in self.reviews:
            raise Exception("Review already exists")

        self.reviews[review_id] = Review(
            id=review_id,
            creator=gl.message.sender_address,
            requirement=requirement,
            evidence_url=evidence_url,
            status="pending",
            confidence=0,
            summary="",
        )

    @gl.public.write
    def resolve_review(self, review_id: str) -> None:
        if review_id not in self.reviews:
            raise Exception("Review not found")

        review = self.reviews[review_id]

        if review.status != "pending":
            raise Exception("Review already resolved")

        verdict = self._evaluate(review.requirement, review.evidence_url)

        confidence = int(verdict.get("confidence", 0))
        if confidence < 0:
            confidence = 0
        if confidence > 100:
            confidence = 100

        approved = bool(verdict.get("approved", False))
        summary = str(verdict.get("summary", ""))[:240]

        review.status = "approved" if approved else "rejected"
        review.confidence = confidence
        review.summary = summary

    @gl.public.view
    def get_review(self, review_id: str) -> Review:
        if review_id not in self.reviews:
            raise Exception("Review not found")
        return self.reviews[review_id]

    @gl.public.view
    def get_reviews(self) -> dict:
        return {key: value for key, value in self.reviews.items()}
