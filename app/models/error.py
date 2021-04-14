from pydantic import BaseModel, Field
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class ApiError(BaseModel):
    message: str = Field(..., description="Error message")

    @staticmethod
    def create_response(status_code: int, message: str) -> JSONResponse:
        error = ApiError(message=message)
        encoded = jsonable_encoder(error)

        return JSONResponse(status_code=status_code, content=encoded)
