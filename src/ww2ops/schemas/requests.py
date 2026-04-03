from pydantic import BaseModel, ConfigDict, Field, EmailStr


class StartSimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_name: str = Field(min_length=3, max_length=200)
    start_year: int = Field(ge=1939, le=1945)
    side: str = Field(pattern="^(axis|allies)$")
    seed: int | None = Field(default=None, ge=1, le=2147483647)


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    simulation_id: int
    decision_type: str = Field(pattern="^(resource_allocation|espionage|military_action|diplomacy)$")
    decision_data: dict


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=6, max_length=128)


class RegisterRequest(LoginRequest):
    email: EmailStr
    role: str = Field(default="historian", pattern="^(historian|commander|analyst)$")
