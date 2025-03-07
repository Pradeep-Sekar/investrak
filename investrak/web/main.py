from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from pathlib import Path
from uuid import UUID
import logging
from typing import Optional
from datetime import datetime, UTC

from investrak.core.storage import JsonFileStorage, StorageError
from investrak.core.models import Portfolio, Goal, InvestmentEntry, InvestmentType
from investrak.core.analytics import PortfolioAnalytics

app = FastAPI(title="InvesTrak")
storage = JsonFileStorage(Path.home() / ".investrak")
templates = Jinja2Templates(directory="investrak/web/templates")
app.mount("/static", StaticFiles(directory="investrak/web/static"), name="static")

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Error processing request: {exc}", exc_info=True)
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error_message": str(exc)},
        status_code=500
    )

@app.get("/")
async def home(request: Request):
    try:
        portfolios = storage.list_portfolios()
        return templates.TemplateResponse(
            "home.html",
            {"request": request, "portfolios": portfolios}
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/create")
async def create_portfolio_form(request: Request):
    """Show the create portfolio form."""
    return templates.TemplateResponse(
        "create_portfolio.html",
        {"request": request}
    )

@app.post("/portfolio/create")
async def create_portfolio(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Process the create portfolio form submission."""
    try:
        portfolio = Portfolio(
            name=name,
            description=description
        )
        
        storage.save_portfolio(portfolio)
        return RedirectResponse(
            url=f"/portfolio/{portfolio.id}",
            status_code=303
        )
    except (StorageError, ValueError) as e:
        return templates.TemplateResponse(
            "create_portfolio.html",
            {
                "request": request,
                "error": str(e)
            },
            status_code=400
        )

@app.get("/portfolio/{portfolio_id}")
async def view_portfolio(request: Request, portfolio_id: UUID):
    try:
        portfolio = storage.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
            
        investments = storage.list_investments(portfolio_id)
        analytics = PortfolioAnalytics(storage)
        metrics = analytics.calculate_portfolio_metrics(portfolio_id)
        
        return templates.TemplateResponse(
            "portfolio.html",
            {
                "request": request,
                "portfolio": portfolio,
                "investments": investments,
                "metrics": metrics
            }
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goals")
async def list_goals(request: Request):
    try:
        goals = storage.list_goals()
        return templates.TemplateResponse(
            "goals.html",
            {"request": request, "goals": goals}
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goals/create")
async def create_goal_form(request: Request):
    """Show the create goal form."""
    return templates.TemplateResponse(
        "create_goal.html",
        {"request": request}
    )

@app.post("/goals/create")
async def create_goal(
    request: Request,
    name: str = Form(...),
    target_amount: float = Form(...),
    target_date: str = Form(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    status: str = Form(...)
):
    """Process the create goal form submission."""
    try:
        # Convert target_date string to datetime
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
        target_date = target_date.replace(tzinfo=UTC)
        
        # Validate target date is in the future
        if target_date <= datetime.now(UTC):
            raise ValueError("Target date must be in the future")

        # Create new goal
        goal = Goal(
            name=name,
            target_amount=target_amount,
            target_date=target_date,
            category=category or None,
            description=description or None,
            status=status
        )
        
        storage.save_goal(goal)
        return RedirectResponse(
            url=f"/goals/{goal.id}",
            status_code=303
        )
    except (StorageError, ValueError) as e:
        return templates.TemplateResponse(
            "create_goal.html",
            {
                "request": request,
                "error": str(e)
            },
            status_code=400
        )

@app.get("/goals/{goal_id}")
async def view_goal(request: Request, goal_id: UUID):
    try:
        goal = storage.get_goal(goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        return templates.TemplateResponse(
            "goal_detail.html",
            {"request": request, "goal": goal}
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/goals/{goal_id}/edit")
async def edit_goal_form(request: Request, goal_id: UUID):
    """Show the edit goal form."""
    try:
        goal = storage.get_goal(goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        return templates.TemplateResponse(
            "edit_goal.html",
            {"request": request, "goal": goal}
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/goals/{goal_id}/edit")
async def update_goal(
    request: Request,
    goal_id: UUID,
    name: str = Form(...),
    target_amount: float = Form(...),
    target_date: str = Form(...),
    category: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    status: str = Form(...)
):
    """Process the edit goal form submission."""
    try:
        goal = storage.get_goal(goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        # Convert target_date string to datetime
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
        target_date = target_date.replace(tzinfo=UTC)  # Add UTC timezone
        
        # Create updated goal
        updated_goal = goal.model_copy(
            update={
                "name": name,
                "target_amount": target_amount,
                "target_date": target_date,
                "category": category or None,
                "description": description or None,
                "status": status
            }
        )
        
        storage.update_goal(updated_goal)
        return RedirectResponse(
            url=f"/goals/{goal_id}",
            status_code=303
        )
    except (StorageError, ValueError) as e:
        return templates.TemplateResponse(
            "edit_goal.html",
            {
                "request": request,
                "goal": goal,
                "error": str(e)
            },
            status_code=400
        )

@app.get("/portfolio/{portfolio_id}/analytics")
async def portfolio_analytics(
    request: Request, 
    portfolio_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    try:
        portfolio = storage.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
            
        analytics = PortfolioAnalytics(storage)
        metrics = analytics.calculate_portfolio_metrics(portfolio_id)
        performance = analytics.calculate_performance_metrics(
            portfolio_id, start_date, end_date
        )
        
        return templates.TemplateResponse(
            "portfolio_analytics.html",
            {
                "request": request,
                "portfolio": portfolio,
                "metrics": metrics,
                "performance": performance
            }
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/{portfolio_id}/add-investment")
async def add_investment_form(request: Request, portfolio_id: UUID):
    """Show the add investment form."""
    try:
        portfolio = storage.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return templates.TemplateResponse(
            "add_investment.html",
            {"request": request, "portfolio": portfolio}
        )
    except StorageError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/portfolio/{portfolio_id}/add-investment")
async def add_investment(
    request: Request,
    portfolio_id: UUID,
    symbol: str = Form(...),
    type: str = Form(...),
    quantity: int = Form(...),
    purchase_price: float = Form(...),
    purchase_date: str = Form(...),
    category: Optional[str] = Form(None),
    notes: Optional[str] = Form(None)
):
    """Process the add investment form submission."""
    try:
        portfolio = storage.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Validate inputs
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if purchase_price <= 0:
            raise ValueError("Purchase price must be positive")
        if len(symbol) > 10:
            raise ValueError("Symbol too long")

        # Convert purchase_date string to datetime
        purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d")
        purchase_date = purchase_date.replace(tzinfo=UTC)

        # Create new investment
        investment = InvestmentEntry(
            portfolio_id=portfolio_id,
            symbol=symbol.upper(),
            type=InvestmentType(type),
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_date=purchase_date,
            category=category,
            notes=notes
        )
        
        storage.save_investment(investment)
        return RedirectResponse(
            url=f"/portfolio/{portfolio_id}",
            status_code=303
        )
    except (StorageError, ValueError) as e:
        return templates.TemplateResponse(
            "add_investment.html",
            {
                "request": request,
                "portfolio": portfolio,
                "error": str(e)
            },
            status_code=400
        )

# The create portfolio routes have been moved to the top
# The view portfolio route has been moved after the create routes
# The rest of the routes remain in the same order
