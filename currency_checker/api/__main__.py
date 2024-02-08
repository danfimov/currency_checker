from currency_checker.api.application import get_app


app = get_app()


if __name__ == "__main__":
    from os import getenv

    from dotenv import load_dotenv
    from uvicorn import run

    load_dotenv('conf/.env')

    run(
        app='currency_checker.api.__main__:app',
        host=getenv('APP__HOST', '127.0.0.1'),
        port=int(getenv('APP__PORT', '8000')),
        reload=bool(getenv('APP__RELOAD', 'True')),
    )
