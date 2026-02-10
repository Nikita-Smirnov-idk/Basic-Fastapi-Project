from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.db.yc_company import YCCompany
from app.domain.entities.db.yc_founder import YCFounder
from app.domain.entities.db.yc_sync_state import YCSyncState


YC_ALL_URL = "https://yc-oss.github.io/api/companies/all.json"


class FoundersHTMLParser(HTMLParser):
    """Parse YC founder blocks from company HTML pages."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_active_founders = False
        self._in_done = False
        self._current: dict[str, Any] | None = None
        self._founders: list[dict[str, Any]] = []
        self._bio_parts: list[str] = []
        self._capture_bio = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # type: ignore[override]
        if self._in_done:
            return
        if not self._in_active_founders:
            return

        attrs_dict = dict(attrs)
        if tag == "img":
            alt = (attrs_dict.get("alt") or "").strip()
            src = (attrs_dict.get("src") or "").strip()
            if not alt or not src:
                return
            if alt.lower() in {"twitter account", "x (twitter) logo"}:
                return
            if "/avatars/" not in src and "avatars" not in src:
                return

            self._flush_current()
            self._current = {
                "name": alt,
                "avatar_url": src,
                "twitter_url": None,
                "linkedin_url": None,
                "yc_profile_url": None,
                "role": None,
                "bio": None,
            }
            self._bio_parts = []
            self._capture_bio = False
            return

        if tag == "a" and self._current:
            href = (attrs_dict.get("href") or "").strip()
            if not href:
                return
            if "twitter.com/" in href or "x.com/" in href:
                self._current["twitter_url"] = self._current["twitter_url"] or href
            elif "linkedin.com/" in href:
                self._current["linkedin_url"] = self._current["linkedin_url"] or href
            elif "/people/" in href or "ycombinator.com/people/" in href:
                self._current["yc_profile_url"] = self._current["yc_profile_url"] or href

    def handle_data(self, data: str) -> None:  # type: ignore[override]
        if self._in_done:
            return
        text = data.strip()
        if not text:
            return

        if text == "Active Founders":
            self._in_active_founders = True
            return
        if text in {"Company Launches", "Jobs at", "Jobs at "} and self._in_active_founders:
            self._in_active_founders = False
            self._in_done = True
            self._flush_current()
            return

        if not self._in_active_founders or not self._current:
            return

        if text in {"Founder", "Co-Founder", "Cofounder", "Co-founder"}:
            self._current["role"] = self._current["role"] or text
            self._capture_bio = True
            return

        if self._capture_bio:
            self._bio_parts.append(text)

    def close(self) -> None:  # type: ignore[override]
        self._flush_current()
        super().close()

    def founders(self) -> list[dict[str, Any]]:
        return self._dedupe(self._founders)

    def _flush_current(self) -> None:
        if not self._current:
            return
        if self._bio_parts and not self._current.get("bio"):
            self._current["bio"] = " ".join(self._bio_parts).strip()[:4000]
        self._founders.append(self._current)
        self._current = None
        self._bio_parts = []
        self._capture_bio = False

    def _dedupe(self, founders: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str, str]] = set()
        out: list[dict[str, Any]] = []
        for f in founders:
            name = (f.get("name") or "").strip()
            if not name:
                continue
            tw = (f.get("twitter_url") or "").strip()
            li = (f.get("linkedin_url") or "").strip()
            key = (name.lower(), tw, li)
            if key in seen:
                continue
            seen.add(key)
            out.append(f)
        return out


async def sync_yc_directory(session: AsyncSession) -> int:
    """Sync YC directory data from the public YC JSON + founders HTML pages."""
    now = datetime.utcnow()
    sync_state = await _get_or_create_sync_state(session)
    sync_state.last_started_at = now
    sync_state.last_error = None

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(YC_ALL_URL)
            resp.raise_for_status()
            data: list[dict[str, Any]] = resp.json()
    except Exception as exc:  # noqa: BLE001
        sync_state.last_finished_at = datetime.utcnow()
        sync_state.last_error = str(exc)
        session.add(sync_state)
        await session.commit()
        raise

    # Truncate existing data before re‑import
    await session.execute(YCFounder.__table__.delete())  # type: ignore[arg-type]
    await session.execute(YCCompany.__table__.delete())  # type: ignore[arg-type]

    companies: list[YCCompany] = []
    for raw in data:
        company = YCCompany(
            yc_id=raw["id"],
            name=raw["name"],
            slug=raw["slug"],
            batch=raw.get("batch") or "",
            batch_code=_batch_code(raw.get("batch")),
            year=_batch_year(raw.get("batch")),
            status=raw.get("status") or "",
            industry=raw.get("industry"),
            subindustry=raw.get("subindustry"),
            website=raw.get("website"),
            all_locations=raw.get("all_locations"),
            one_liner=raw.get("one_liner"),
            long_description=raw.get("long_description"),
            team_size=raw.get("team_size"),
            small_logo_thumb_url=raw.get("small_logo_thumb_url"),
            url=raw.get("url") or "",
            is_hiring=bool(raw.get("isHiring")),
            nonprofit=bool(raw.get("nonprofit")),
            top_company=bool(raw.get("top_company")),
            industries=list(raw.get("industries") or []),
            regions=list(raw.get("regions") or []),
            tags=list(raw.get("tags") or []),
            launched_at=raw.get("launched_at"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        companies.append(company)

    session.add_all(companies)
    await session.commit()

    founder_count = await _sync_founders(session)

    sync_state.last_finished_at = datetime.utcnow()
    sync_state.last_success_at = sync_state.last_finished_at
    sync_state.last_item_count = len(companies)
    session.add(sync_state)
    await session.commit()

    return len(companies)


async def _sync_founders(session: AsyncSession) -> int:
    stmt = select(YCCompany.id, YCCompany.url).where(YCCompany.url != "")
    rows = (await session.execute(stmt)).all()

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        import asyncio

        sem = asyncio.Semaphore(15)

        async def fetch_one(company_id, url: str) -> list[YCFounder]:
            async with sem:
                try:
                    resp = await client.get(
                        url,
                        headers={
                            "User-Agent": "FeatureBoardAppYCsync/1.0",
                            "Accept": "text/html,application/xhtml+xml",
                        },
                    )
                    resp.raise_for_status()
                except Exception:
                    return []
                parser = FoundersHTMLParser()
                parser.feed(resp.text)
                parser.close()
                founders_raw = parser.founders()
                founders: list[YCFounder] = []
                for idx, f in enumerate(founders_raw):
                    founders.append(
                        YCFounder(
                            company_id=company_id,
                            sort_order=idx,
                            name=f.get("name") or "",
                            role=f.get("role"),
                            bio=f.get("bio"),
                            yc_profile_url=f.get("yc_profile_url"),
                            twitter_url=f.get("twitter_url"),
                            linkedin_url=f.get("linkedin_url"),
                            avatar_url=(f.get("avatar_url") or "").split("?", 1)[0] or None,
                        )
                    )
                return founders

        def chunks(seq, size: int):
            for i in range(0, len(seq), size):
                yield seq[i : i + size]

        total = 0
        for batch in chunks(rows, 50):
            tasks = [fetch_one(company_id=row[0], url=row[1]) for row in batch]
            results = await asyncio.gather(*tasks)
            founders_models: list[YCFounder] = []
            for founders in results:
                founders_models.extend(founders)
            if founders_models:
                session.add_all(founders_models)
                await session.commit()
                total += len(founders_models)

        return total


async def _get_or_create_sync_state(session: AsyncSession) -> YCSyncState:
    stmt = select(YCSyncState).where(YCSyncState.source == "yc_directory")
    result = await session.execute(stmt)
    existing = result.scalars().first()
    if existing:
        return existing
    sync_state = YCSyncState(source="yc_directory")
    session.add(sync_state)
    await session.commit()
    await session.refresh(sync_state)
    return sync_state


def _batch_code(batch: str | None) -> str:
    if not batch:
        return ""
    parts = batch.split()
    if len(parts) != 2:
        return ""
    season, year_str = parts
    short = "W" if season.lower().startswith("winter") else "S"
    try:
        year = int(year_str)
    except ValueError:
        return ""
    return f"{short}{year}"


def _batch_year(batch: str | None) -> int:
    if not batch:
        return 0
    parts = batch.split()
    if len(parts) != 2:
        return 0
    try:
        return int(parts[1])
    except ValueError:
        return 0

