import pandas as pd

from app.database.db import engine


def load_cantina_metrics(
    company_id: str
):
    query = """
        SELECT
            c.id,
            c.name,

            COALESCE((
                SELECT SUM(s.total)
                FROM "Sale" s
                WHERE s."cantinaId" = c.id
                  AND s.status = 'COMPLETED'
            ), 0) AS revenue,

            COALESCE((
                SELECT SUM(co.amount)
                FROM "Cost" co
                WHERE co."cantinaId" = c.id
            ), 0) AS expenses

        FROM "Cantina" c
        WHERE c."companyId" = %(company_id)s
    """

    df = pd.read_sql(
        query,
        engine,
        params={
            "company_id": company_id
        }
    )

    if df.empty:
        return []

    cantinas = []

    for _, row in df.iterrows():
        cantinas.append({
            "id": row["id"],

            "name": row["name"],

            "revenue": float(
                row["revenue"] or 0
            ),

            "expenses": float(
                row["expenses"] or 0
            ),

            # temporaire
            "growth": 0,
        })

    return cantinas