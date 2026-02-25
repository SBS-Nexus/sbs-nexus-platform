from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.rechnungsverarbeitung.src.api.main import app as invoice_app
from modules.hydraulikdoc.src.api.main import app as hydraulik_app
from modules.auftragsai.src.api.main import app as auftragsai_app

platform = FastAPI(
    title="SBS NEXUS Platform API",
    description="Dokumenten-intelligente KI-Plattform für Industrie-KMU",
    version="0.1.0",
)

platform.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # [TECH-DEBT] Vor Production auf Domain einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modul-Router mounten
platform.mount("/api/v1/rechnungen", invoice_app)
platform.mount("/api/v1/hydraulik", hydraulik_app)
platform.mount("/api/v1/auftraege", auftragsai_app)


@platform.get("/health")
async def health():
    return {
        "status": "ok",
        "platform": "sbs-nexus",
        "modules": ["rechnungsverarbeitung", "hydraulikdoc", "auftragsai"],
    }


@platform.get("/")
async def root():
    return {
        "platform": "SBS NEXUS",
        "version": "0.1.0",
        "docs": "/docs",
    }
