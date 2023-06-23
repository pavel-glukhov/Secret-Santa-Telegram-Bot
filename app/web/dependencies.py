from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from app.web.schemes import AuthJWTSettings


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()


def get_current_user(Authorize: AuthJWT = Depends()):
    # TODO убрать заглушку при переводе на вебхуки
    # "---------------------------------------------------------------"
    # Заглушка#
    user = 245942576
    return user
    # "---------------------------------------------------------------"
    # Процесс нормальной проверки
    # "---------------------------------------------------------------"

    # try:
    #
    #     Authorize.jwt_required()
    #     current_user = Authorize.get_jwt_subject()
    # except Exception as e:
    #     current_user = None
    #
    #
    # return current_user
