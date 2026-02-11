from fastapi import APIRouter, HTTPException, Request, status, BackgroundTasks

from app.domain.entities.db.user import User
from app.transport.http.deps import CurrentUser, SessionDep
from app.transport.http.rate_limit import limiter
from app.transport.schemas import (
    YCFounderPublic,
    YCCompanyPublic,
    YCCompaniesPublic,
    YCSearchMeta,
    YCSyncStatePublic,
    Message,
)
from app.use_cases.ports.yc_directory_repository import YCSearchFilters
from app.transport.http.routes.yc.deps import YCDirectoryUseCaseDep


router = APIRouter(prefix="/yc", tags=["yc"])


FREE_TIER_LIMIT = 15
PAID_PAGE_SIZE = 50


def _is_paid(user: User) -> bool:
    return user.plan != "free" or user.balance_cents > 0


@router.get("/companies", response_model=YCCompaniesPublic)
@limiter.limit("2/second")
async def list_companies(
    request: Request,
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    yc_uc: YCDirectoryUseCaseDep,
    q: str | None = None,
    batch: str | None = None,
    year: int | None = None,
    status_filter: str | None = None,
    industry: str | None = None,
    is_hiring: bool | None = None,
    nonprofit: bool | None = None,
    top_company: bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> YCCompaniesPublic:
    background_tasks.add_task(yc_uc.ensure_auto_sync)

    if _is_paid(current_user):
        skip = max(0, skip)
        limit = min(max(1, limit), PAID_PAGE_SIZE)
    else:
        skip = 0
        limit = FREE_TIER_LIMIT

    filters = YCSearchFilters(
        q=q,
        batch=batch,
        year=year,
        status=status_filter,
        industry=industry,
        is_hiring=is_hiring,
        nonprofit=nonprofit,
        top_company=top_company,
    )

    items, count = await yc_uc.list_companies(filters=filters, skip=skip, limit=limit)

    company_ids = [item.id for item in items]
    founders_by_company: dict[str, list[YCFounderPublic]] = {}
    if company_ids:
        founders = await yc_uc.get_founders_for_company_ids(company_ids)
        for f in founders:
            key = str(f.company_id)
            founders_by_company.setdefault(key, []).append(
                YCFounderPublic(
                    name=f.name or "",
                    twitter_url=f.twitter_url,
                    linkedin_url=f.linkedin_url,
                )
            )

    data = [
        YCCompanyPublic(
            yc_id=item.yc_id,
            name=item.name,
            slug=item.slug,
            batch=item.batch,
            batch_code=item.batch_code,
            year=item.year,
            status=item.status,
            industry=item.industry,
            website=item.website,
            all_locations=item.all_locations,
            one_liner=item.one_liner,
            team_size=item.team_size,
            small_logo_thumb_url=item.small_logo_thumb_url,
            url=item.url,
            is_hiring=item.is_hiring,
            nonprofit=item.nonprofit,
            top_company=item.top_company,
            tags=item.tags,
            industries=item.industries or [],
            regions=item.regions or [],
            founders=founders_by_company.get(str(item.id), []),
        )
        for item in items
    ]

    if current_user.plan == "pay_per_use" and data and _is_paid(current_user):
        current_user.balance_cents = max(0, current_user.balance_cents - 10)
        session.add(current_user)
        await session.commit()

    return YCCompaniesPublic(data=data, count=count)


@router.get("/meta", response_model=YCSearchMeta)
@limiter.limit("2/second")
async def get_meta(
    request: Request,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    yc_uc: YCDirectoryUseCaseDep,
) -> YCSearchMeta:
    background_tasks.add_task(yc_uc.ensure_auto_sync)
    meta = await yc_uc.get_meta()
    return YCSearchMeta(
        years=meta["years"],
        batches=meta["batches"],
        statuses=meta["statuses"],
        industries=meta["industries"],
    )
