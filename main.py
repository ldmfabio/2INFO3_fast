import logging

from fastapi import FastAPI, HTTPException, Path, Query, Request, Response
from fastapi.responses import JSONResponse
from mysql.connector import Error as MySQLError

from database import executar_sql

app = FastAPI(title="API de produtos — Aula 1")


@app.exception_handler(MySQLError)
def erro_de_banco(request: Request, exc: MySQLError):
    logging.getLogger("uvicorn.error").error("Erro no MySQL: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Não foi possível acessar o banco de dados."},
    )


def representar_produto(produto):
    return {
        "id": produto["id"],
        "nome": produto["nome"],
        "categoria": produto["categoria"],
        "preco": format(produto["preco"], ".2f"),
    }

@app.get("/produtos")
def listar_produtos():
    sql = "SELECT id, nome, categoria, preco FROM produtos ORDER BY id"
    produtos = executar_sql(sql)

    return {
        "dados": [representar_produto(produto) for produto in produtos],
        "sintaxesql": {"sql": sql, "parametros": []},
    }

@app.get("/produtos/{produto_id}")
def consultar_produto(produto_id: int = Path(gt=0)):
    sql = "SELECT * FROM produtos WHERE id = %s"
    parametros = (produto_id,)
    produtos = executar_sql(sql, parametros)

    if not produtos:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    return {
        "dados": representar_produto(produtos[0]),
        "sintaxesql": {"sql": sql, "parametros": list(parametros)},
    }

@app.get("/produtos_categoria")
def listar_produtos_por_categoria(
    categoria: str | None = Query(default=None, min_length=1, max_length=50),
):
    sql = "SELECT * FROM produtos"
    parametros = ()

    if categoria is not None:
        sql += " WHERE categoria = %s"
        parametros = (categoria,)

    produtos = executar_sql(sql, parametros)

    return {
        "dados": [representar_produto(produto) for produto in produtos],
        "sintaxesql": {"sql": sql, "parametros": list(parametros)},
    }
