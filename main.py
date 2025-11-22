from fastapi import FastAPI, Depends, HTTPException, status
import models
from database import engine, get_db
from sqlalchemy.orm import Session
import schemas
import datetime
import utils
from datetime import datetime, timedelta
from oauth2 import create_access_token, get_current_user
from typing import Annotated
from sqlalchemy import or_

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.post("/register", response_model=schemas.Token)
def register_user(new_user: schemas.UserRegister, db: Session = Depends(get_db)):

    if (
        db.query(models.User)
        .filter(
            or_(models.User.email == new_user.email, models.User.name == new_user.name)
        )
        .first()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/Name was already registered",
        )

    hashed_password = utils.get_password_hash(new_user.password)

    user = models.User(
        name=new_user.name, email=new_user.email, hashed_password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=schemas.Token)
def log_in_user(user_to_login: schemas.UserLogin, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.name == user_to_login.name).first()
    if not user or not utils.authenticate_user(user, user_to_login.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/expense", response_model=schemas.AddExpenseOut)
def add_expense(
    new_expense: schemas.AddExpense,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):

    now = datetime.today().date()
    expense = models.Expense(**new_expense.dict(), date=now, owner_id=current_user.id)

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@app.put("/expenses/{id}", response_model=schemas.UpdatedExpenseOut)
def update_expense(
    id: int,
    updated_expense: schemas.UpdatedExpense,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):

    expense_query = db.query(models.Expense).filter(models.Expense.id == id)

    expense_to_update = expense_query.first()
    if not expense_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id: {id} does not exist",
        )
    if expense_to_update.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You have no permission"
        )

    updated_data = updated_expense.dict(exclude_unset=True)
    updated_data["updated_at"] = datetime.now()
    expense_query.update(updated_data, synchronize_session=False)
    db.commit()

    updated_expense = expense_query.first()
    return updated_expense


@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):

    expense_query = db.query(models.Expense).filter(models.Expense.id == id)
    expense_to_delete = expense_query.first()

    if not expense_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with id: {id} does not exist",
        )
    if expense_to_delete.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You have no permission"
        )

    expense_query.delete(synchronize_session=False)
    db.commit()
    return


@app.get("/expenses", response_model=schemas.ExpensesOut)
async def list_expenses(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    last: str = None,
):
    date_filter = datetime(1, 1, 1)
    if last == "week":
        date_filter = datetime.now() - timedelta(days=7)
    elif last == "month":
        date_filter = datetime.now() - timedelta(days=30)
    elif last == "3month":
        date_filter = datetime.now() - timedelta(days=91)

    expenses = (
        db.query(models.Expense)
        .filter(
            models.Expense.created_at >= date_filter,
            models.Expense.owner_id == current_user.id,
        )
        .all()
    )
    return {"Expenses": expenses}
