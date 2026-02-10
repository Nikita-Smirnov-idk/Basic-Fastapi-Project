from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.domain.entities.db.user import User
from app.domain.entities.db.yc_company import YCCompany
from app.domain.entities.db.yc_founder import YCFounder
from app.transport.http.deps import CurrentUser, SessionDep
from app.transport.schemas import (
    YCFounderPublic,
    YCCompanyPublic,
    YCCompaniesPublic,
    YCSearchMeta,
    YCSyncStatePublic,
    Message,
)
from app.use_cases.use_cases.yc_directory_use_case import (
    YCDirectoryUseCase,
    YCSearchFilters,
)


router = APIRouter(prefix="/yc", tags=["yc"])


def get_yc_use_case(session: SessionDep) -> YCDirectoryUseCase:
    return YCDirectoryUseCase(session=session)


def _require_paid_or_balance(user: User) -> None:
    if user.plan == "free" and user.balance_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Upgrade plan or top up balance to use YC directory",
        )


@router.get("/companies", response_model=YCCompaniesPublic)
async def list_companies(
    session: SessionDep,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    yc_uc: YCDirectoryUseCase = Depends(get_yc_use_case),
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
    _require_paid_or_balance(current_user)

    # Автоматический синк запускается в фоне и не блокирует ответ
    background_tasks.add_task(yc_uc.ensure_auto_sync)

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
        f_stmt = (
            select(YCFounder)
            .where(YCFounder.company_id.in_(company_ids))
            .order_by(YCFounder.company_id, YCFounder.sort_order)
        )
        f_result = await session.execute(f_stmt)
        founders = f_result.scalars().all()
        for f in founders:
            key = str(f.company_id)
            founders_by_company.setdefault(key, []).append(
                YCFounderPublic(
                    name=f.name,
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
            founders=founders_by_company.get(str(item.id), []),
        )
        for item in items
    ]

    if current_user.plan == "pay_per_use" and data:
        current_user.balance_cents = max(0, current_user.balance_cents - 10)
        session.add(current_user)
        await session.commit()

    return YCCompaniesPublic(data=data, count=count)


@router.get("/meta", response_model=YCSearchMeta)
async def get_meta(
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    yc_uc: YCDirectoryUseCase = Depends(get_yc_use_case),
) -> YCSearchMeta:
    _require_paid_or_balance(current_user)
    background_tasks.add_task(yc_uc.ensure_auto_sync)
    meta = await yc_uc.get_meta()
    return YCSearchMeta(
        years=meta["years"],
        batches=meta["batches"],
        statuses=meta["statuses"],
        industries=meta["industries"],
    )


@router.get("/export")
async def export_csv(
    current_user: CurrentUser,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    yc_uc: YCDirectoryUseCase = Depends(get_yc_use_case),
) -> Response:
    _require_paid_or_balance(current_user)

    # Обновляем данные в фоне, не блокируя экспорт
    background_tasks.add_task(yc_uc.ensure_auto_sync)

    stmt = select(YCCompany).order_by(YCCompany.batch_code.desc(), YCCompany.name.asc())
    result = await session.execute(stmt)
    items = result.scalars().all()

    headers = [
        "id",
        "name",
        "slug",
        "batch",
        "year",
        "status",
        "industry",
        "team_size",
        "website",
        "all_locations",
        "one_liner",
        "founders",
        "founders_twitter",
        "is_hiring",
        "nonprofit",
        "top_company",
    ]
    lines = [",".join(headers)]
    for c in items:
        f_stmt = (
            select(YCFounder)
            .where(YCFounder.company_id == c.id)
            .order_by(YCFounder.sort_order)
        )
        f_result = await session.execute(f_stmt)
        founders = f_result.scalars().all()
        founder_names = ";".join([f.name for f in founders]).replace(",", " ")
        founder_twitters = ";".join([f.twitter_url or "" for f in founders]).replace(",", " ")
        row = [
            str(c.yc_id),
            c.name.replace(",", " "),
            c.slug,
            c.batch,
            str(c.year),
            c.status,
            (c.industry or "").replace(",", " "),
            str(c.team_size or ""),
            (c.website or "").replace(",", " "),
            (c.all_locations or "").replace(",", " "),
            (c.one_liner or "").replace(",", " "),
            founder_names,
            founder_twitters,
            "1" if c.is_hiring else "0",
            "1" if c.nonprofit else "0",
            "1" if c.top_company else "0",
        ]
        lines.append(",".join(row))

    content = "\n".join(lines)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="yc_companies.csv"'},
    )


@router.post("/sync", response_model=Message)
async def sync_now(
    current_user: CurrentUser,
    yc_uc: YCDirectoryUseCase = Depends(get_yc_use_case),
) -> Message:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can trigger sync",
        )
    count = await yc_uc.sync_from_source()
    return Message(message=f"Synced {count} YC companies")


@router.get("/sync-state", response_model=YCSyncStatePublic)
async def get_sync_state(
    current_user: CurrentUser,
    yc_uc: YCDirectoryUseCase = Depends(get_yc_use_case),
) -> YCSyncStatePublic:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view sync state",
        )
    state = await yc_uc.get_sync_state()
    if not state:
        return YCSyncStatePublic(
            last_started_at=None,
            last_finished_at=None,
            last_success_at=None,
            last_error=None,
            last_item_count=None,
        )
    return YCSyncStatePublic(
        last_started_at=state.last_started_at,
        last_finished_at=state.last_finished_at,
        last_success_at=state.last_success_at,
        last_error=state.last_error,
        last_item_count=state.last_item_count,
    )

