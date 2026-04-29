import csv
import io
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resource import Resource

REQUIRED_COLUMNS = {"name", "email", "role", "seniority", "team_id"}


async def import_roster_csv(file_bytes: bytes, db: AsyncSession) -> dict:
    reader = csv.DictReader(io.StringIO(file_bytes.decode("utf-8")))
    cols = set(reader.fieldnames or [])
    if not REQUIRED_COLUMNS.issubset(cols):
        missing = REQUIRED_COLUMNS - cols
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    imported, skipped = 0, 0
    errors: list[dict] = []

    for row in reader:
        try:
            r = Resource(
                name=row["name"].strip(),
                email=row["email"].strip().lower(),
                role=row["role"].strip(),
                seniority=row.get("seniority", "mid").strip(),
                team_id=row["team_id"].strip(),
                skills=row.get("skills", "") or None,
            )
            db.add(r)
            imported += 1
        except Exception as e:
            skipped += 1
            errors.append({"row": dict(row), "error": str(e)})
    await db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}
