"""Seed products from dunnhumby dataset into the data service."""

import os
import subprocess
from pathlib import Path

import pandas as pd
from constants import PRODUCTS_FILE, SEED_BATCH_SIZE, SEED_MAX_PRODUCTS
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.crud.product import product_crud
from shared.schemas.product import ProductCreate


class SeedProducts:
    """Downloads and seeds dunnhumby products directly into the database."""

    def download_if_missing(self) -> None:
        """Download dunnhumby product file from Kaggle if not present."""
        if Path(PRODUCTS_FILE).exists():
            print("Product file already exists. Skipping download.")
            return

        print("Downloading dunnhumby product.csv from Kaggle...")
        Path("data").mkdir(exist_ok=True)

        from shared.config import settings

        os.environ["KAGGLE_API_TOKEN"] = settings.kaggle_api_token

        result = subprocess.run(
            [
                "kaggle",
                "datasets",
                "download",
                "frtgnn/dunnhumby-the-complete-journey",
                "-p",
                "data/",
                "--file",
                "product.csv",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Kaggle download failed: {result.stderr}")

        subprocess.run(
            ["unzip", "-o", "data/product.csv.zip", "-d", "data/"],
            check=True,
        )
        print("Download complete.")

    def load_and_clean(self) -> list[ProductCreate]:
        """Load and clean product CSV."""
        print(f"Loading {PRODUCTS_FILE}...")
        df = pd.read_csv(PRODUCTS_FILE)
        df = df.dropna(subset=["COMMODITY_DESC"])
        df = df[df["COMMODITY_DESC"] != "NO COMMODITY DESCRIPTION"]
        df = df.drop_duplicates(subset=["PRODUCT_ID"])
        df = df.head(SEED_MAX_PRODUCTS)
        print(f"Loaded {len(df)} products after cleaning.")
        return [
            ProductCreate(
                product_id=str(row["PRODUCT_ID"]),
                commodity_desc=str(row["COMMODITY_DESC"]),
                sub_commodity_desc=str(row.get("SUB_COMMODITY_DESC", "")),
                department=str(row.get("DEPARTMENT", "")),
            )
            for _, row in df.iterrows()
        ]

    async def run(self, db: AsyncSession) -> None:
        """Run the full seed process."""
        self.download_if_missing()
        products = self.load_and_clean()
        existing = await product_crud.count(db)
        if existing > 0:
            print(f"Products already seeded ({existing} rows). Skipping.")
            return

        print(f"Seeding {len(products)} products...")
        total = 0
        for i in range(0, len(products), SEED_BATCH_SIZE):
            batch = products[i : i + SEED_BATCH_SIZE]
            items = await product_crud.bulk_create(db, batch)
            await db.commit()
            total += len(items)
            print(f"Seeded {total}/{len(products)}...")

        print(f"Done. {total} products seeded.")
