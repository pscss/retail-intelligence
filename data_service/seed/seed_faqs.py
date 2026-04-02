"""Seed FAQs from Bitext dataset into the data service."""

from constants import SEED_BATCH_SIZE, SEED_MAX_FAQS
from datasets import load_dataset
from sqlalchemy.ext.asyncio import AsyncSession

from data_service.crud.faq import faq_crud
from shared.schemas.faq import FAQCreate


class SeedFaqs:
    """Downloads and seeds Bitext FAQs directly into the database."""

    DATASET_NAME = "bitext/Bitext-customer-support-llm-chatbot-training-dataset"

    def download_and_prepare(self) -> list[FAQCreate]:
        """Load FAQs from HuggingFace datasets."""
        print(f"Loading FAQ dataset from HuggingFace: {self.DATASET_NAME}...")
        ds = load_dataset(self.DATASET_NAME, split="train")
        df = ds.to_pandas()

        df = df[["instruction", "response", "intent"]].dropna()
        df = df.drop_duplicates(subset=["instruction"])
        df = df.head(SEED_MAX_FAQS)

        print(f"Loaded {len(df)} FAQs after cleaning.")
        return [
            FAQCreate(
                question=str(row["instruction"]),
                answer=str(row["response"]),
                intent_label=str(row["intent"]),
                source="bitext",
            )
            for _, row in df.iterrows()
        ]

    async def run(self, db: AsyncSession) -> None:
        """Run the full FAQ seed process."""
        faqs = self.download_and_prepare()
        existing = await faq_crud.count(db)
        if existing > 0:
            print(f"FAQs already seeded ({existing} rows). Skipping.")
            return

        print(f"Seeding {len(faqs)} FAQs...")
        total = 0
        for i in range(0, len(faqs), SEED_BATCH_SIZE):
            batch = faqs[i : i + SEED_BATCH_SIZE]
            items = await faq_crud.bulk_create(db, batch)
            await db.commit()
            total += len(items)
            print(f"Seeded {total}/{len(faqs)}...")

        print(f"Done. {total} FAQs seeded.")
