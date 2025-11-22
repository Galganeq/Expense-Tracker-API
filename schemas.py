from pydantic import BaseModel, Field
from datetime import datetime, date as DateExpense
from typing import List


class Expense(BaseModel):

    description: str
    amount: float
    category: str


class AddExpense(Expense):
    pass


class AddExpenseOut(Expense):
    created_at: datetime
    date: DateExpense = Field(default_factory=DateExpense.today)
    id: int

    class Config:
        from_attributes = True


class UpdatedExpense(Expense):
    pass


class UpdatedExpenseOut(Expense):
    updated_at: datetime
    id: int
    date: DateExpense = Field(default_factory=DateExpense.today)

    class Config:
        from_attributes = True


class ExpenseOut(Expense):
    updated_at: datetime
    created_at: datetime
    date: DateExpense = Field(default_factory=DateExpense.today)


class ExpensesOut(BaseModel):
    Expenses: List[ExpenseOut]


class User(BaseModel):

    name: str
    password: str


class UserPublic(BaseModel):
    name: str
    id: int
    email: str


class UserRegister(User):

    email: str


class UserLogin(User):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str
