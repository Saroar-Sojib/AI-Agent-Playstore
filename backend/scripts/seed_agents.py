from __future__ import annotations

import asyncio
import csv
import re
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.infrastructure.database import AsyncSessionLocal  # noqa: E402
from app.modules.agents.models.agent import Agent  # noqa: E402
from app.modules.agents.models.sub_agent import SubAgent  # noqa: E402

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "agents_sample.csv"


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "agent"


def build_agent_system_prompt(industry: str, profession: str, tasks: list[str]) -> str:
    """Derive a persona system prompt purely from the row's own data."""
    task_lines = "\n".join(f"- {t}" for t in tasks if t)
    return (
        f"You are an AI assistant persona playing the role of a {profession} "
        f"working in the {industry} industry.\n\n"
        f"Your core responsibilities include:\n{task_lines}\n\n"
        f"Always answer in character as a knowledgeable, professional {profession}. "
        f"Be precise, practical, and grounded in real {industry} practice. "
        f"If asked something clearly outside a {profession}'s professional scope, "
        f"say so and steer the conversation back to your area of expertise."
    )


def build_sub_agent_system_prompt(
    industry: str, profession: str, sub_agent_name: str, task: str
) -> str:
    """Derive a specialized sub-agent prompt from its own name + task text."""
    return (
        f"You are the {sub_agent_name}, a specialized AI assistant that supports "
        f"a {profession} in the {industry} industry.\n\n"
        f"Your specific focus: {task}\n\n"
        f"Stay strictly within this specialization — go deep rather than broad. "
        f"If the user asks about something that belongs to a different aspect of "
        f"{profession} work, briefly note that and suggest the relevant specialized "
        f"assistant, rather than answering outside your focus."
    )


def load_rows(csv_path: Path) -> list[dict]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        return [row for row in csv.DictReader(f) if row.get("Profession")]


async def seed(csv_path: Path) -> None:
    rows = load_rows(csv_path)
    print(f"Loaded {len(rows)} rows from {csv_path}")

    async with AsyncSessionLocal() as db:
        created, updated = 0, 0
        for row in rows:
            source_row_no = int(row["#"])
            industry = row["Industry"].strip()
            profession = row["Profession"].strip()
            tasks = [row.get(f"Task {i}", "").strip() for i in range(1, 5)]

            agent_prompt = build_agent_system_prompt(industry, profession, tasks)

            result = await db.execute(
                select(Agent).where(Agent.source_row_no == source_row_no)
            )
            agent = result.scalar_one_or_none()
            if agent is None:
                agent = Agent(
                    slug=slugify(profession),
                    industry=industry,
                    profession=profession,
                    system_prompt=agent_prompt,
                    source_row_no=source_row_no,
                )
                db.add(agent)
                await db.flush()
                created += 1
            else:
                agent.industry = industry
                agent.profession = profession
                agent.system_prompt = agent_prompt
                updated += 1

            for i in range(1, 5):
                name = row.get(f"Agent {i}", "").strip()
                task = row.get(f"Agent {i} Task", "").strip()
                if not name:
                    continue
                sub_prompt = build_sub_agent_system_prompt(
                    industry, profession, name, task
                )
                result = await db.execute(
                    select(SubAgent).where(
                        SubAgent.agent_id == agent.id, SubAgent.order_index == i
                    )
                )
                sub_agent = result.scalar_one_or_none()
                if sub_agent is None:
                    db.add(
                        SubAgent(
                            agent_id=agent.id,
                            name=name,
                            task_description=task,
                            system_prompt=sub_prompt,
                            order_index=i,
                        )
                    )
                else:
                    sub_agent.name = name
                    sub_agent.task_description = task
                    sub_agent.system_prompt = sub_prompt

        await db.commit()
        print(f"Agents created: {created}, updated: {updated}")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not path.exists():
        sys.exit(f"CSV not found: {path}")
    asyncio.run(seed(path))
