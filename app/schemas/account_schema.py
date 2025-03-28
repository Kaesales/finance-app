from pydantic import BaseModel, Field, field_validator, model_validator
from decimal import Decimal
from typing import Literal, Optional
from enum import Enum

class AccountType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class AccountCreate(BaseModel):
    """
    Schema para criação de contas bancárias.
    
    Campos obrigatórios:
    - name: Nome da conta (2-50 caracteres)
    - is_credit: Define se é conta de crédito
    
    Campos condicionais:
    - credit_limit: Obrigatório para contas de crédito
    - due_day: Obrigatório para contas de crédito (1-31)
    """
    name: str = Field(..., min_length=2, max_length=50, example="Conta Corrente")
    is_credit: bool = Field(
        False,
        description="Define se é conta de crédito (default=False)"
    )
    credit_limit: Optional[Decimal] = Field(
        None,
        description="Limite de crédito (obrigatório para contas de crédito)"
    )
    due_day: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Dia de vencimento (1-31, obrigatório para contas de crédito)"
    )
    balance: Optional[Decimal] = Field(
        None,
        description = "Saldo da Conta"
    )


    @field_validator('due_day')
    def validate_due_day(cls, v, values):
        if values.data.get('is_credit') and v is None:
            raise ValueError("Dia de vencimento é obrigatório para contas de crédito")
        return v

   
class AccountResponse(BaseModel):
    """
    Schema de resposta para contas bancárias.
    Inclui todos os campos de criação mais:
    - id: Identificador único
    - balance: Saldo atual
    - user_id: ID do usuário dono da conta
    """
    id: int = Field(..., example=1)
    name: str = Field(..., example="Conta Corrente")
    is_credit: bool = Field(..., example=False)
    balance: Decimal = Field(..., example=1000.50)
    user_id: int = Field(..., example=1)
    credit_limit: Optional[Decimal] = Field(None, example=5000.00)
    due_day: Optional[int] = Field(None, example=10)

class AccountUpdate(BaseModel):
    """
    Schema para atualização de contas bancárias com validações condicionais
    """
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        example="Conta Corrente Atualizada"
    )
    is_credit: Optional[bool] = Field(
        None,
        description="Define se é conta de crédito (True/False)"
    )
    balance: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Novo saldo (apenas para contas débito)"
    )
    credit_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Novo limite (apenas para contas crédito)"
    )
    due_day: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="Novo dia de vencimento (apenas para contas crédito)"
    )

    @model_validator(mode='after')
    def validate_type_fields(self):

        # Se is_credit for modificado na requisição
        if self.is_credit is not None:
            if self.is_credit: 
                if self.balance is not None:
                    raise ValueError("Contas de crédito não podem ter saldo")
                if self.credit_limit is None or self.credit_limit <= 0:
                    raise ValueError("Contas de crédito requerem um limite positivo")
                if self.due_day is None:
                    raise ValueError("Contas de crédito precisam de um dia de vencimento")
            else:  # Conta de débito
                if self.credit_limit is not None:
                    raise ValueError("Contas de débito não podem ter limite de crédito")
                if self.due_day is not None:
                    raise ValueError("Contas de débito não podem ter dia de vencimento")
                if self.balance is None or self.balance <= 0:
                    raise ValueError("Contas de débito requerem um saldo positivo")

        # Validações para atualizações parciais
        else:
            if self.credit_limit is not None and self.due_day is None:
                raise ValueError("Ao atualizar limite, informe também o dia de vencimento")
            if self.due_day is not None and self.credit_limit is None:
                raise ValueError("Ao atualizar vencimento, informe também o limite")

        return self
    
    class Config:
        from_attributes = True  # Permite conversão de ORM para Pydantic