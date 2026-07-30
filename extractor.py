from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field


class GrantFacts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(description="本文に明記された制度名称")
    target: str | None = Field(description="本文に明記された対象者。簡潔に列挙")
    amount: str | None = Field(description="本文に明記された支給額、上限額、補助率")
    deadline: str | None = Field(description="本文に明記された申請期限。原文の日付表現を保持")


SYSTEM_PROMPT = """あなたは自治体公式文書から事実だけを転記する抽出器です。
要約、解説、推測、補完、言い換え、宣伝文句を一切生成しないでください。
入力本文に明記された制度名称、対象者、金額・補助率、期限だけを抽出してください。
本文に根拠がない項目、判断できない項目は必ずnullにしてください。
複数制度が混在する場合は、ページの主題である制度だけを対象にしてください。"""


def extract_grant(*, text: str, prefecture: str, city: str, source_url: str, updated_at: str) -> dict[str, Any] | None:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    completion = client.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"以下の自治体公式ページ本文から抽出してください。\n\n{text}"},
        ],
        response_format=GrantFacts,
    )
    message = completion.choices[0].message
    if message.refusal or not message.parsed or not message.parsed.title:
        return None
    facts = json.loads(message.parsed.model_dump_json())
    return {
        **facts,
        "prefecture": prefecture,
        "city": city,
        "source_url": source_url,
        "updated_at": updated_at,
    }
